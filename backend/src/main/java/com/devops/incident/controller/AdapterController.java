package com.devops.incident.controller;

import com.devops.incident.adapter.ToolAdapter;
import com.devops.incident.adapter.ToolAdapterFactory;
import com.devops.incident.adapter.ToolQuery;
import com.devops.incident.exception.AdapterException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.HashMap;
import java.util.Map;

/**
 * Adapter endpoints invoked by the AI Service to fetch evidence. Requests are routed
 * to the configured adapter (simulator or real) via the {@link ToolAdapterFactory}.
 */
@Slf4j
@RestController
@RequestMapping("/api/adapters")
public class AdapterController {

    private final ToolAdapterFactory adapterFactory;

    public AdapterController(ToolAdapterFactory adapterFactory) {
        this.adapterFactory = adapterFactory;
    }

    @GetMapping("/kubernetes")
    public ResponseEntity<Map<String, Object>> kubernetes(
            @RequestParam(required = false) String services,
            @RequestParam(required = false) String namespace,
            @RequestParam(required = false) String types,
            @RequestParam(required = false) String since,
            @RequestParam(required = false) String until) {
        Map<String, String> filters = new HashMap<>();
        if (types != null) {
            filters.put("types", types);
        }
        return fetch("kubernetes", services, namespace, since, until, filters);
    }

    @GetMapping("/logs")
    public ResponseEntity<Map<String, Object>> logs(
            @RequestParam(required = false) String services,
            @RequestParam(required = false) String level,
            @RequestParam(required = false) String type,
            @RequestParam(required = false) String since,
            @RequestParam(required = false) String until,
            @RequestParam(required = false) Integer limit) {
        Map<String, String> filters = new HashMap<>();
        if (level != null) {
            filters.put("level", level);
        }
        if (type != null) {
            filters.put("type", type);
        }
        if (limit != null) {
            filters.put("limit", String.valueOf(limit));
        }
        return fetch("logs", services, null, since, until, filters);
    }

    @GetMapping("/metrics")
    public ResponseEntity<Map<String, Object>> metrics(
            @RequestParam(required = false) String services,
            @RequestParam(required = false) String metrics,
            @RequestParam(required = false) String from,
            @RequestParam(required = false) String to,
            @RequestParam(required = false) String step) {
        Map<String, String> filters = new HashMap<>();
        if (metrics != null) {
            filters.put("metrics", metrics);
        }
        if (step != null) {
            filters.put("step", step);
        }
        return fetch("metrics", services, null, from, to, filters);
    }

    @GetMapping("/git")
    public ResponseEntity<Map<String, Object>> git(
            @RequestParam(required = false) String services,
            @RequestParam(required = false) String since,
            @RequestParam(required = false) String until,
            @RequestParam(required = false) Integer limit) {
        Map<String, String> filters = new HashMap<>();
        if (limit != null) {
            filters.put("limit", String.valueOf(limit));
        }
        return fetch("git", services, null, since, until, filters);
    }

    private ResponseEntity<Map<String, Object>> fetch(String type, String services, String namespace,
                                                       String from, String to, Map<String, String> filters) {
        ToolAdapter adapter = adapterFactory.getAdapter(type);
        ToolQuery query = ToolQuery.builder()
                .service(services)
                .namespace(namespace)
                .from(parseInstant(from))
                .to(parseInstant(to))
                .filters(filters)
                .build();
        try {
            return ResponseEntity.ok(adapter.fetchData(query).join());
        } catch (Exception e) {
            log.error("Adapter {} fetch failed: {}", type, e.getMessage());
            throw new AdapterException(type + " adapter failed: " + rootMessage(e));
        }
    }

    private Instant parseInstant(String value) {
        if (value == null || value.isBlank()) {
            return null;
        }
        try {
            return Instant.parse(value);
        } catch (Exception e) {
            throw new IllegalArgumentException("Invalid ISO 8601 timestamp: " + value);
        }
    }

    private String rootMessage(Throwable e) {
        Throwable cause = e;
        while (cause.getCause() != null) {
            cause = cause.getCause();
        }
        return cause.getMessage();
    }
}
