package com.devops.incident.service;

import com.devops.incident.exception.ResourceNotFoundException;
import com.devops.incident.integration.AIServiceClient;
import com.devops.incident.integration.dto.AIAnalysisResult;
import com.devops.incident.integration.dto.AIEvidencePayload;
import com.devops.incident.integration.dto.AIInvestigationRequest;
import com.devops.incident.integration.dto.AIRecommendedAction;
import com.devops.incident.model.Action;
import com.devops.incident.model.Incident;
import com.devops.incident.model.Investigation;
import com.devops.incident.model.InvestigationEvidence;
import com.devops.incident.model.dto.request.TriggerInvestigationRequest;
import com.devops.incident.model.dto.response.ActionResponse;
import com.devops.incident.model.dto.response.EvidenceResponse;
import com.devops.incident.model.dto.response.InvestigationResponse;
import com.devops.incident.model.enums.ActionStatus;
import com.devops.incident.model.enums.ActionType;
import com.devops.incident.model.enums.IncidentStatus;
import com.devops.incident.model.enums.InvestigationStatus;
import com.devops.incident.repository.ActionRepository;
import com.devops.incident.repository.EvidenceRepository;
import com.devops.incident.repository.IncidentRepository;
import com.devops.incident.repository.InvestigationRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Slf4j
@Service
public class InvestigationService {

    private static final List<String> DEFAULT_SCOPE = List.of("kubernetes", "logs", "metrics", "git");

    private final InvestigationRepository investigationRepository;
    private final EvidenceRepository evidenceRepository;
    private final ActionRepository actionRepository;
    private final IncidentRepository incidentRepository;
    private final AIServiceClient aiServiceClient;
    private final EventPublisherService eventPublisher;
    private final String callbackBaseUrl;

    /**
     * Self-reference (proxy) so that {@link #callAiServiceAsync} is invoked through the
     * Spring proxy and runs on a separate thread instead of synchronously.
     */
    private final InvestigationService self;

    public InvestigationService(InvestigationRepository investigationRepository,
                                EvidenceRepository evidenceRepository,
                                ActionRepository actionRepository,
                                IncidentRepository incidentRepository,
                                AIServiceClient aiServiceClient,
                                EventPublisherService eventPublisher,
                                @Value("${app.callback-base-url:http://localhost:8080}") String callbackBaseUrl,
                                @org.springframework.context.annotation.Lazy InvestigationService self) {
        this.investigationRepository = investigationRepository;
        this.evidenceRepository = evidenceRepository;
        this.actionRepository = actionRepository;
        this.incidentRepository = incidentRepository;
        this.aiServiceClient = aiServiceClient;
        this.eventPublisher = eventPublisher;
        this.callbackBaseUrl = callbackBaseUrl;
        this.self = self;
    }

    public InvestigationResponse trigger(String incidentId, TriggerInvestigationRequest request) {
        Incident incident = incidentRepository.findById(incidentId)
                .orElseThrow(() -> ResourceNotFoundException.of("Incident", incidentId));

        Instant now = Instant.now();
        Investigation investigation = Investigation.builder()
                .id(UUID.randomUUID().toString())
                .incidentId(incidentId)
                .status(InvestigationStatus.PENDING)
                .createdAt(now)
                .updatedAt(now)
                .build();
        investigationRepository.save(investigation);

        // Transition incident to INVESTIGATING if currently OPEN.
        if (incident.getStatus() == IncidentStatus.OPEN) {
            incident.setStatus(IncidentStatus.INVESTIGATING);
            incident.setUpdatedAt(Instant.now());
            incidentRepository.update(incident);
        }

        InvestigationResponse response = InvestigationResponse.from(investigation);
        eventPublisher.publishInvestigationEvent("INVESTIGATION_STARTED", incidentId, investigation.getId(), response);

        List<String> scope = (request != null && request.getScope() != null && !request.getScope().isEmpty())
                ? request.getScope() : DEFAULT_SCOPE;
        self.callAiServiceAsync(investigation.getId(), incident, scope);

        return response;
    }

    @Async
    public void callAiServiceAsync(String investigationId, Incident incident, List<String> scope) {
        try {
            markInProgress(investigationId);
            AIInvestigationRequest aiRequest = AIInvestigationRequest.builder()
                    .investigationId(investigationId)
                    .incidentId(incident.getId())
                    .incident(AIInvestigationRequest.IncidentContext.builder()
                            .title(incident.getTitle())
                            .description(incident.getDescription())
                            .severity(incident.getSeverity().name())
                            .affectedServices(incident.getAffectedServices())
                            .build())
                    .callbackUrl(callbackBaseUrl + "/api/internal/investigations/" + investigationId + "/callback")
                    .scope(scope)
                    .build();
            aiServiceClient.startInvestigation(aiRequest);
            log.info("AI investigation {} accepted by AI service", investigationId);
        } catch (Exception e) {
            log.error("Failed to start AI investigation {}: {}", investigationId, e.getMessage());
            failInvestigation(investigationId, "Failed to start AI investigation: " + e.getMessage());
        }
    }

    private void markInProgress(String investigationId) {
        investigationRepository.findById(investigationId).ifPresent(inv -> {
            inv.setStatus(InvestigationStatus.IN_PROGRESS);
            inv.setStartedAt(Instant.now());
            inv.setUpdatedAt(Instant.now());
            investigationRepository.update(inv);
            eventPublisher.publishInvestigationEvent("INVESTIGATION_PROGRESS", inv.getIncidentId(),
                    investigationId, InvestigationResponse.from(inv));
        });
    }

    public void failInvestigation(String investigationId, String reason) {
        investigationRepository.findById(investigationId).ifPresent(inv -> {
            inv.setStatus(InvestigationStatus.FAILED);
            inv.setSummary(reason);
            inv.setCompletedAt(Instant.now());
            inv.setUpdatedAt(Instant.now());
            investigationRepository.update(inv);
            eventPublisher.publishInvestigationEvent("INVESTIGATION_FAILED", inv.getIncidentId(),
                    investigationId, InvestigationResponse.from(inv));
        });
    }

    /**
     * Processes the callback delivered by the AI service when investigation completes.
     */
    public InvestigationResponse processCallback(String investigationId, AIAnalysisResult result) {
        Investigation inv = investigationRepository.findById(investigationId)
                .orElseThrow(() -> ResourceNotFoundException.of("Investigation", investigationId));

        boolean failed = result.getStatus() != null && result.getStatus().equalsIgnoreCase("FAILED");
        inv.setStatus(failed ? InvestigationStatus.FAILED : InvestigationStatus.COMPLETED);
        inv.setSummary(result.getSummary());
        inv.setRootCause(result.getRootCause());
        inv.setConfidence(result.getConfidence());
        inv.setAiModelUsed(result.getAiModelUsed());
        inv.setCompletedAt(Instant.now());
        inv.setUpdatedAt(Instant.now());
        investigationRepository.update(inv);

        // Store evidence
        if (result.getEvidence() != null) {
            for (AIEvidencePayload ev : result.getEvidence()) {
                InvestigationEvidence evidence = InvestigationEvidence.builder()
                        .id(UUID.randomUUID().toString())
                        .investigationId(investigationId)
                        .source(ev.getSource())
                        .type(ev.getType())
                        .data(ev.getData() == null ? "{}" : ev.getData().toString())
                        .collectedAt(Instant.now())
                        .build();
                evidenceRepository.save(evidence);
            }
        }

        // Create proposed actions
        if (result.getRecommendedActions() != null) {
            for (AIRecommendedAction ra : result.getRecommendedActions()) {
                Instant now = Instant.now();
                Action action = Action.builder()
                        .id(UUID.randomUUID().toString())
                        .investigationId(investigationId)
                        .incidentId(inv.getIncidentId())
                        .type(parseActionType(ra.getType()))
                        .status(ActionStatus.PROPOSED)
                        .title(ra.getTitle())
                        .description(ra.getDescription())
                        .command(ra.getCommand())
                        .targetService(ra.getTargetService())
                        .parameters(ra.getParameters() == null ? null : ra.getParameters().toString())
                        .risk(ra.getRisk())
                        .estimatedImpact(ra.getEstimatedImpact())
                        .createdAt(now)
                        .updatedAt(now)
                        .build();
                actionRepository.save(action);
            }
        }

        String eventType = failed ? "INVESTIGATION_FAILED" : "INVESTIGATION_COMPLETED";
        InvestigationResponse response = getDetailed(inv.getIncidentId(), investigationId);
        eventPublisher.publishInvestigationEvent(eventType, inv.getIncidentId(), investigationId, response);
        log.info("Processed AI callback for investigation {} -> {}", investigationId, inv.getStatus());
        return response;
    }

    public List<InvestigationResponse> listByIncident(String incidentId) {
        if (!incidentRepository.existsById(incidentId)) {
            throw ResourceNotFoundException.of("Incident", incidentId);
        }
        return investigationRepository.findByIncidentId(incidentId).stream()
                .map(InvestigationResponse::from).toList();
    }

    public InvestigationResponse getDetailed(String incidentId, String investigationId) {
        Investigation inv = investigationRepository.findById(investigationId)
                .orElseThrow(() -> ResourceNotFoundException.of("Investigation", investigationId));
        if (!inv.getIncidentId().equals(incidentId)) {
            throw ResourceNotFoundException.of("Investigation", investigationId);
        }
        InvestigationResponse response = InvestigationResponse.from(inv);
        List<EvidenceResponse> evidence = evidenceRepository.findByInvestigationId(investigationId).stream()
                .map(EvidenceResponse::from).toList();
        List<ActionResponse> actions = actionRepository.findByInvestigationId(investigationId).stream()
                .map(ActionResponse::from).toList();
        response.setEvidence(evidence);
        response.setActions(actions);
        return response;
    }

    public List<EvidenceResponse> getEvidence(String incidentId, String investigationId) {
        Investigation inv = investigationRepository.findById(investigationId)
                .orElseThrow(() -> ResourceNotFoundException.of("Investigation", investigationId));
        if (!inv.getIncidentId().equals(incidentId)) {
            throw ResourceNotFoundException.of("Investigation", investigationId);
        }
        return evidenceRepository.findByInvestigationId(investigationId).stream()
                .map(EvidenceResponse::from).toList();
    }

    private ActionType parseActionType(String type) {
        if (type == null) {
            return ActionType.CUSTOM;
        }
        try {
            return ActionType.valueOf(type.trim().toUpperCase());
        } catch (IllegalArgumentException e) {
            return ActionType.CUSTOM;
        }
    }
}
