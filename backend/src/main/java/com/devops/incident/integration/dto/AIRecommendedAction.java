package com.devops.incident.integration.dto;

import com.fasterxml.jackson.databind.JsonNode;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AIRecommendedAction {
    private String type;
    private String title;
    private String description;
    private String command;
    private String targetService;
    private JsonNode parameters;
    private String risk;
    private String estimatedImpact;
}
