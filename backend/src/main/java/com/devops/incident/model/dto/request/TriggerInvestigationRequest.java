package com.devops.incident.model.dto.request;

import lombok.Data;

import java.util.List;

@Data
public class TriggerInvestigationRequest {
    private String priority;
    private List<String> scope;
}
