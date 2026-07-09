package com.devops.incident.model;

import com.devops.incident.model.enums.ReportFormat;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Report {
    private String id;
    private String incidentId;
    private String title;
    private String content;
    private ReportFormat format;
    private String metadata;
    private Instant generatedAt;
    private Instant createdAt;
}
