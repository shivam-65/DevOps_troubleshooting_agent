package com.devops.incident.adapter;

import com.devops.incident.integration.SimulatorClient;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;

/**
 * Base class for simulated adapters that proxy evidence requests to the Simulator service.
 */
public abstract class AbstractSimulatedAdapter implements ToolAdapter {

    protected final SimulatorClient simulatorClient;

    protected AbstractSimulatedAdapter(SimulatorClient simulatorClient) {
        this.simulatorClient = simulatorClient;
    }

    @Override
    public CompletableFuture<Map<String, Object>> fetchData(ToolQuery query) {
        MultiValueMap<String, String> params = new LinkedMultiValueMap<>();
        if (query != null) {
            if (query.getService() != null) {
                params.add("services", query.getService());
            }
            if (query.getNamespace() != null) {
                params.add("namespace", query.getNamespace());
            }
            if (query.getType() != null) {
                params.add("type", query.getType());
            }
            if (query.getFrom() != null) {
                params.add("since", query.getFrom().toString());
            }
            if (query.getTo() != null) {
                params.add("until", query.getTo().toString());
            }
            if (query.getFilters() != null) {
                query.getFilters().forEach(params::add);
            }
        }
        return CompletableFuture.supplyAsync(() -> simulatorClient.fetch(getType(), params));
    }

    @Override
    public CompletableFuture<Map<String, Object>> executeAction(ToolAction action) {
        // Simulated execution: acknowledge the action and echo back parameters.
        Map<String, Object> result = new HashMap<>();
        result.put("status", "SUCCESS");
        result.put("adapter", getType());
        result.put("actionType", action == null ? null : action.getType());
        result.put("service", action == null ? null : action.getService());
        result.put("message", "Simulated execution completed successfully");
        return CompletableFuture.completedFuture(result);
    }

    @Override
    public boolean isAvailable() {
        return simulatorClient.isAvailable();
    }
}
