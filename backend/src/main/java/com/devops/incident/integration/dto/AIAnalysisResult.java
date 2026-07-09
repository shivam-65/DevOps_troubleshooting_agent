package com.devops.incident.integration.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Payload sent by the AI Service to the backend callback endpoint when an
 * investigation completes (or fails).
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AIAnalysisResult {
    private String investigationId;
    private String status;          // COMPLETED | FAILED
    private String summary;
    private String rootCause;
    private Double confidence;
    private String aiModelUsed;
    private List<AIEvidencePayload> evidence;
    private List<AIRecommendedAction> recommendedActions;
}
