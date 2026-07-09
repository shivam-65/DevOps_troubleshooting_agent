package com.devops.incident.model;

import com.devops.incident.model.enums.InvestigationStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Investigation {
    private String id;
    private String incidentId;
    private InvestigationStatus status;
    private String summary;
    private String rootCause;
    private Double confidence;
    private String aiModelUsed;
    private Instant startedAt;
    private Instant completedAt;
    private Instant createdAt;
    private Instant updatedAt;
}
