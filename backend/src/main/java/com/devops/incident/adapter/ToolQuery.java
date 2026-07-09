package com.devops.incident.adapter;

import lombok.Builder;
import lombok.Data;

import java.time.Instant;
import java.util.Map;

@Data
@Builder
public class ToolQuery {
    private String type;
    private String service;
    private String namespace;
    private Instant from;
    private Instant to;
    private Map<String, String> filters;
}
