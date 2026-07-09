package com.devops.incident.model.dto.response;

import com.devops.incident.model.Action;
import com.devops.incident.model.enums.ActionStatus;
import com.devops.incident.model.enums.ActionType;
import com.devops.incident.util.JsonUtil;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ActionResponse {
    private String id;
    private String investigationId;
    private String incidentId;
    private ActionType type;
    private ActionStatus status;
    private String title;
    private String description;
    private String command;
    private String targetService;
    private Map<String, Object> parameters;
    private String risk;
    private String estimatedImpact;
    private Object executionResult;
    private String approvedBy;
    private Instant approvedAt;
    private Instant executedAt;
    private Instant completedAt;
    private Instant createdAt;
    private Instant updatedAt;

    public static ActionResponse from(Action action) {
        return ActionResponse.builder()
                .id(action.getId())
                .investigationId(action.getInvestigationId())
                .incidentId(action.getIncidentId())
                .type(action.getType())
                .status(action.getStatus())
                .title(action.getTitle())
                .description(action.getDescription())
                .command(action.getCommand())
                .targetService(action.getTargetService())
                .parameters(JsonUtil.toMap(action.getParameters()))
                .risk(action.getRisk())
                .estimatedImpact(action.getEstimatedImpact())
                .executionResult(JsonUtil.toObject(action.getExecutionResult()))
                .approvedBy(action.getApprovedBy())
                .approvedAt(action.getApprovedAt())
                .executedAt(action.getExecutedAt())
                .completedAt(action.getCompletedAt())
                .createdAt(action.getCreatedAt())
                .updatedAt(action.getUpdatedAt())
                .build();
    }
}
