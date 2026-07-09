package com.devops.incident.model.dto.response;

import com.devops.incident.model.Report;
import com.devops.incident.model.enums.ReportFormat;
import com.devops.incident.util.JsonUtil;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ReportResponse {
    private String id;
    private String incidentId;
    private String title;
    private String content;
    private ReportFormat format;
    private Object metadata;
    private Instant generatedAt;
    private Instant createdAt;

    public static ReportResponse from(Report report) {
        return ReportResponse.builder()
                .id(report.getId())
                .incidentId(report.getIncidentId())
                .title(report.getTitle())
                .content(report.getContent())
                .format(report.getFormat())
                .metadata(JsonUtil.toObject(report.getMetadata()))
                .generatedAt(report.getGeneratedAt())
                .createdAt(report.getCreatedAt())
                .build();
    }
}
