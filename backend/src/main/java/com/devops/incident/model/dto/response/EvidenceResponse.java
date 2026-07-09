package com.devops.incident.model.dto.response;

import com.devops.incident.model.InvestigationEvidence;
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
public class EvidenceResponse {
    private String id;
    private String investigationId;
    private String source;
    private String type;
    private Object data;
    private Instant collectedAt;

    public static EvidenceResponse from(InvestigationEvidence evidence) {
        return EvidenceResponse.builder()
                .id(evidence.getId())
                .investigationId(evidence.getInvestigationId())
                .source(evidence.getSource())
                .type(evidence.getType())
                .data(JsonUtil.toObject(evidence.getData()))
                .collectedAt(evidence.getCollectedAt())
                .build();
    }
}
