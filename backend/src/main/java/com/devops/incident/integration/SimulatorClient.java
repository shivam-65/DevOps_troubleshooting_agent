package com.devops.incident.integration;

import com.devops.incident.exception.AdapterException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.Duration;
import java.util.Map;

/**
 * Thin HTTP client for the Simulator service. Used by the simulated tool adapters
 * to fetch evidence from {@code /api/adapters/{type}}.
 */
@Slf4j
@Component
public class SimulatorClient {

    private final WebClient webClient;

    public SimulatorClient(WebClient.Builder builder,
                           @Value("${adapters.simulator.base-url:http://localhost:8001}") String baseUrl) {
        this.webClient = builder.baseUrl(baseUrl).build();
    }

    @SuppressWarnings("unchecked")
    public Map<String, Object> fetch(String type, MultiValueMap<String, String> queryParams) {
        try {
            return webClient.get()
                    .uri(uriBuilder -> uriBuilder
                            .path("/api/adapters/" + type)
                            .queryParams(queryParams == null ? new LinkedMultiValueMap<>() : queryParams)
                            .build())
                    .retrieve()
                    .bodyToMono(new org.springframework.core.ParameterizedTypeReference<Map<String, Object>>() {})
                    .timeout(Duration.ofSeconds(30))
                    .block();
        } catch (Exception e) {
            log.error("Simulator fetch failed for type {}: {}", type, e.getMessage());
            throw new AdapterException("Simulator adapter '" + type + "' unavailable: " + e.getMessage(), e);
        }
    }

    public boolean isAvailable() {
        try {
            webClient.get().uri("/health").retrieve().toBodilessEntity().timeout(Duration.ofSeconds(3)).block();
            return true;
        } catch (Exception e) {
            return false;
        }
    }
}
