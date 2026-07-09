package com.devops.incident.adapter;

import lombok.Builder;
import lombok.Data;

import java.util.Map;

@Data
@Builder
public class ToolAction {
    private String type;
    private String service;
    private String namespace;
    private Map<String, Object> parameters;
}
