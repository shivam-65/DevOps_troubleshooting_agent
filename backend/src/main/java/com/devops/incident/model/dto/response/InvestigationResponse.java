package com.devops.incident.model.dto.response;

import com.devops.incident.model.Investigation;
import com.devops.incident.model.enums.InvestigationStatus;
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
public class InvestigationResponse {
    private String id;
    private String incidentId;
    private InvestigationStatus status;
    private String summary;
    private String rootCause;
    private Double confidence;
    private String aiModelUsed;
    private List<EvidenceResponse> evidence;
    private List<ActionResponse> actions;
    private Instant startedAt;
    private Instant completedAt;
    private Instant createdAt;
    private Instant updatedAt;

    public static InvestigationResponse from(Investigation investigation) {
        return InvestigationResponse.builder()
                .id(investigation.getId())
                .incidentId(investigation.getIncidentId())
                .status(investigation.getStatus())
                .summary(investigation.getSummary())
                .rootCause(investigation.getRootCause())
                .confidence(investigation.getConfidence())
                .aiModelUsed(investigation.getAiModelUsed())
                .startedAt(investigation.getStartedAt())
                .completedAt(investigation.getCompletedAt())
                .createdAt(investigation.getCreatedAt())
                .updatedAt(investigation.getUpdatedAt())
                .build();
    }
}
