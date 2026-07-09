package com.devops.incident.model;

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
public class Incident {
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
}
