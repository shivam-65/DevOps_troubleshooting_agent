package com.devops.incident.model;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class InvestigationEvidence {
    private String id;
    private String investigationId;
    private String source;
    private String type;
    private String data;
    private Instant collectedAt;
}
