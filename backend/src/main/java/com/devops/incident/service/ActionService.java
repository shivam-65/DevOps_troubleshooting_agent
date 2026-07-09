package com.devops.incident.service;

import com.devops.incident.adapter.ToolAction;
import com.devops.incident.adapter.ToolAdapter;
import com.devops.incident.adapter.ToolAdapterFactory;
import com.devops.incident.exception.InvalidStateTransitionException;
import com.devops.incident.exception.ResourceNotFoundException;
import com.devops.incident.model.Action;
import com.devops.incident.model.dto.request.ApproveActionRequest;
import com.devops.incident.model.dto.request.CreateActionRequest;
import com.devops.incident.model.dto.request.RejectActionRequest;
import com.devops.incident.model.dto.response.ActionResponse;
import com.devops.incident.model.dto.response.PagedResponse;
import com.devops.incident.model.enums.ActionStatus;
import com.devops.incident.model.enums.ActionType;
import com.devops.incident.repository.ActionRepository;
import com.devops.incident.repository.IncidentRepository;
import com.devops.incident.repository.InvestigationRepository;
import com.devops.incident.util.JsonUtil;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Slf4j
@Service
public class ActionService {

    private final ActionRepository actionRepository;
    private final InvestigationRepository investigationRepository;
    private final IncidentRepository incidentRepository;
    private final ToolAdapterFactory adapterFactory;
    private final EventPublisherService eventPublisher;

    public ActionService(ActionRepository actionRepository,
                         InvestigationRepository investigationRepository,
                         IncidentRepository incidentRepository,
                         ToolAdapterFactory adapterFactory,
                         EventPublisherService eventPublisher) {
        this.actionRepository = actionRepository;
        this.investigationRepository = investigationRepository;
        this.incidentRepository = incidentRepository;
        this.adapterFactory = adapterFactory;
        this.eventPublisher = eventPublisher;
    }

    public ActionResponse create(CreateActionRequest request) {
        if (investigationRepository.findById(request.getInvestigationId()).isEmpty()) {
            throw ResourceNotFoundException.of("Investigation", request.getInvestigationId());
        }
        if (!incidentRepository.existsById(request.getIncidentId())) {
            throw ResourceNotFoundException.of("Incident", request.getIncidentId());
        }
        Instant now = Instant.now();
        Action action = Action.builder()
                .id(UUID.randomUUID().toString())
                .investigationId(request.getInvestigationId())
                .incidentId(request.getIncidentId())
                .type(request.getType())
                .status(ActionStatus.PROPOSED)
                .title(request.getTitle())
                .description(request.getDescription())
                .command(request.getCommand())
                .targetService(request.getTargetService())
                .parameters(JsonUtil.toJson(request.getParameters()))
                .risk(request.getRisk())
                .estimatedImpact(request.getEstimatedImpact())
                .createdAt(now)
                .updatedAt(now)
                .build();
        actionRepository.save(action);
        log.info("Created action {} ({}) for investigation {}", action.getId(), action.getType(),
                action.getInvestigationId());
        return ActionResponse.from(action);
    }

    public ActionResponse getById(String id) {
        return ActionResponse.from(findOrThrow(id));
    }

    public PagedResponse<ActionResponse> list(String incidentId, String investigationId, ActionStatus status,
                                              int page, int size) {
        List<ActionResponse> content = actionRepository.findAll(incidentId, investigationId, status, page, size)
                .stream().map(ActionResponse::from).toList();
        long total = actionRepository.count(incidentId, investigationId, status);
        return PagedResponse.of(content, page, size, total);
    }

    public ActionResponse approve(String id, ApproveActionRequest request) {
        Action action = findOrThrow(id);
        requireStatus(action, ActionStatus.PROPOSED);
        action.setStatus(ActionStatus.APPROVED);
        action.setApprovedBy(request.getApprovedBy());
        action.setApprovedAt(Instant.now());
        action.setUpdatedAt(Instant.now());
        actionRepository.update(action);
        log.info("Action {} approved by {}", id, request.getApprovedBy());
        ActionResponse response = ActionResponse.from(action);
        eventPublisher.publishActionEvent("ACTION_APPROVED", id, response);
        return response;
    }

    public ActionResponse reject(String id, RejectActionRequest request) {
        Action action = findOrThrow(id);
        if (action.getStatus() != ActionStatus.PROPOSED && action.getStatus() != ActionStatus.APPROVED) {
            throw new InvalidStateTransitionException(
                    "Action can only be rejected from PROPOSED or APPROVED. Current: " + action.getStatus());
        }
        action.setStatus(ActionStatus.REJECTED);
        String reason = request == null ? null : request.getReason();
        action.setExecutionResult(JsonUtil.toJson(Map.of("rejectionReason", reason == null ? "" : reason)));
        action.setUpdatedAt(Instant.now());
        actionRepository.update(action);
        log.info("Action {} rejected", id);
        ActionResponse response = ActionResponse.from(action);
        eventPublisher.publishActionEvent("ACTION_REJECTED", id, response);
        return response;
    }

    public ActionResponse execute(String id) {
        Action action = findOrThrow(id);
        requireStatus(action, ActionStatus.APPROVED);
        action.setStatus(ActionStatus.EXECUTING);
        action.setExecutedAt(Instant.now());
        action.setUpdatedAt(Instant.now());
        actionRepository.update(action);
        ActionResponse response = ActionResponse.from(action);
        eventPublisher.publishActionEvent("ACTION_EXECUTING", id, response);
        runAction(action.getId());
        return response;
    }

    @Async
    public void runAction(String actionId) {
        Action action = actionRepository.findById(actionId).orElse(null);
        if (action == null) {
            return;
        }
        try {
            ToolAdapter adapter = adapterFactory.getAdapter(adapterTypeFor(action.getType()));
            ToolAction toolAction = ToolAction.builder()
                    .type(toolActionTypeFor(action.getType()))
                    .service(action.getTargetService())
                    .parameters(JsonUtil.toMap(action.getParameters()))
                    .build();
            Map<String, Object> result = adapter.executeAction(toolAction).join();
            action.setStatus(ActionStatus.COMPLETED);
            action.setExecutionResult(JsonUtil.toJson(result));
            action.setCompletedAt(Instant.now());
            action.setUpdatedAt(Instant.now());
            actionRepository.update(action);
            log.info("Action {} completed", actionId);
            eventPublisher.publishActionEvent("ACTION_COMPLETED", actionId, ActionResponse.from(action));
        } catch (Exception e) {
            log.error("Action {} execution failed: {}", actionId, e.getMessage());
            action.setStatus(ActionStatus.FAILED);
            action.setExecutionResult(JsonUtil.toJson(Map.of("error", e.getMessage() == null ? "unknown" : e.getMessage())));
            action.setCompletedAt(Instant.now());
            action.setUpdatedAt(Instant.now());
            actionRepository.update(action);
            eventPublisher.publishActionEvent("ACTION_FAILED", actionId, ActionResponse.from(action));
        }
    }

    private String adapterTypeFor(ActionType type) {
        return switch (type) {
            case RESTART_SERVICE, SCALE_UP, ROLLBACK_DEPLOYMENT, FAILOVER, APPLY_CONFIG_CHANGE -> "kubernetes";
            case CLEAR_CACHE -> "kubernetes";
            default -> "kubernetes";
        };
    }

    private String toolActionTypeFor(ActionType type) {
        return switch (type) {
            case RESTART_SERVICE -> "restart_pods";
            case SCALE_UP -> "scale_deployment";
            case ROLLBACK_DEPLOYMENT -> "rollback_deployment";
            case CLEAR_CACHE -> "clear_cache";
            case FAILOVER -> "failover";
            case APPLY_CONFIG_CHANGE -> "apply_config";
            case RUN_SCRIPT -> "run_script";
            case CUSTOM -> "custom";
        };
    }

    private void requireStatus(Action action, ActionStatus required) {
        if (action.getStatus() != required) {
            throw new InvalidStateTransitionException(
                    "Action must be in " + required + " state. Current: " + action.getStatus());
        }
    }

    private Action findOrThrow(String id) {
        return actionRepository.findById(id)
                .orElseThrow(() -> ResourceNotFoundException.of("Action", id));
    }
}
