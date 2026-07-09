package com.devops.incident.model.dto.response;

import com.devops.incident.model.Incident;
import com.devops.incident.model.enums.IncidentSeverity;
import com.devops.incident.model.enums.IncidentStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IncidentResponse {
    private String id;
    private String title;
    private String description;
    private IncidentSeverity severity;
    private IncidentStatus status;
    private List<String> affectedServices;
    private String assignee;
    private List<String> tags;
    private Instant createdAt;
    private Instant updatedAt;
    private Instant resolvedAt;
    private Instant closedAt;

    public static IncidentResponse from(Incident incident) {
        return IncidentResponse.builder()
                .id(incident.getId())
                .title(incident.getTitle())
                .description(incident.getDescription())
                .severity(incident.getSeverity())
                .status(incident.getStatus())
                .affectedServices(incident.getAffectedServices())
                .assignee(incident.getAssignee())
                .tags(incident.getTags())
                .createdAt(incident.getCreatedAt())
                .updatedAt(incident.getUpdatedAt())
                .resolvedAt(incident.getResolvedAt())
                .closedAt(incident.getClosedAt())
                .build();
    }
}
