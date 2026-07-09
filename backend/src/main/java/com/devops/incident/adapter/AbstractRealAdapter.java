package com.devops.incident.adapter;

import com.devops.incident.exception.AdapterException;

import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * Base class for real tool adapters. Real integrations (kubeconfig, Elasticsearch,
 * Prometheus, GitHub) are not part of the MVP and currently report unavailable.
 */
public abstract class AbstractRealAdapter implements ToolAdapter {

    @Override
    public CompletableFuture<Map<String, Object>> fetchData(ToolQuery query) {
        CompletableFuture<Map<String, Object>> future = new CompletableFuture<>();
        future.completeExceptionally(new AdapterException(
                "Real " + getType() + " adapter is not configured in this environment"));
        return future;
    }

    @Override
    public CompletableFuture<Map<String, Object>> executeAction(ToolAction action) {
        CompletableFuture<Map<String, Object>> future = new CompletableFuture<>();
        future.completeExceptionally(new AdapterException(
                "Real " + getType() + " adapter is not configured in this environment"));
        return future;
    }

    @Override
    public boolean isAvailable() {
        return false;
    }
}
