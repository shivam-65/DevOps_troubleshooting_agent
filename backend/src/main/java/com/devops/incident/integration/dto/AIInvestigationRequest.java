package com.devops.incident.integration.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AIInvestigationRequest {
    private String investigationId;
    private String incidentId;
    private IncidentContext incident;
    private String callbackUrl;
    private List<String> scope;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class IncidentContext {
        private String title;
        private String description;
        private String severity;
        private List<String> affectedServices;
    }
}
