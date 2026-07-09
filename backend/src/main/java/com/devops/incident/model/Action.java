package com.devops.incident.model;

import com.devops.incident.model.enums.ActionStatus;
import com.devops.incident.model.enums.ActionType;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Action {
    private String id;
    private String investigationId;
    private String incidentId;
    private ActionType type;
    private ActionStatus status;
    private String title;
    private String description;
    private String command;
    private String targetService;
    private String parameters;
    private String risk;
    private String estimatedImpact;
    private String executionResult;
    private String approvedBy;
    private Instant approvedAt;
    private Instant executedAt;
    private Instant completedAt;
    private Instant createdAt;
    private Instant updatedAt;
}
