package com.devops.incident.adapter;

import java.util.Map;
import java.util.concurrent.CompletableFuture;

public interface ToolAdapter {

    /** @return adapter type: "kubernetes", "logs", "metrics", "git" */
    String getType();

    CompletableFuture<Map<String, Object>> fetchData(ToolQuery query);

    CompletableFuture<Map<String, Object>> executeAction(ToolAction action);

    boolean isAvailable();
}
