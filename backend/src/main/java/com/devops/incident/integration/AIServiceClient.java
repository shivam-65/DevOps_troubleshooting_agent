package com.devops.incident.integration;

import com.devops.incident.exception.AIServiceException;
import com.devops.incident.integration.dto.AIInvestigationRequest;
import com.devops.incident.integration.dto.AIInvestigationResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import reactor.util.retry.Retry;

import java.time.Duration;

/**
 * Client for the Python AI Service. Triggers investigations; results are delivered
 * asynchronously via the backend callback endpoint.
 */
@Slf4j
@Component
public class AIServiceClient {

    private final WebClient webClient;
    private final int maxAttempts;
    private final Duration backoff;
    private final Duration readTimeout;

    public AIServiceClient(WebClient.Builder builder,
                           @Value("${ai-service.base-url:http://localhost:8000}") String baseUrl,
                           @Value("${ai-service.retry.max-attempts:3}") int maxAttempts,
                           @Value("${ai-service.retry.backoff:1s}") Duration backoff,
                           @Value("${ai-service.timeout.read:300s}") Duration readTimeout) {
        this.webClient = builder.baseUrl(baseUrl).build();
        this.maxAttempts = maxAttempts;
        this.backoff = backoff;
        this.readTimeout = readTimeout;
    }

    /**
     * Sends the investigation request to the AI service. Returns the acknowledgement.
     * Retries with exponential backoff on failure.
     */
    public AIInvestigationResponse startInvestigation(AIInvestigationRequest request) {
        try {
            return webClient.post()
                    .uri("/api/investigate")
                    .bodyValue(request)
                    .retrieve()
                    .bodyToMono(AIInvestigationResponse.class)
                    .timeout(readTimeout)
                    .retryWhen(Retry.backoff(Math.max(0, maxAttempts - 1), backoff)
                            .filter(this::isRetryable))
                    .onErrorResume(ex -> Mono.error(
                            new AIServiceException("Failed to start AI investigation: " + ex.getMessage(), ex)))
                    .block();
        } catch (AIServiceException e) {
            throw e;
        } catch (Exception e) {
            throw new AIServiceException("Failed to start AI investigation: " + e.getMessage(), e);
        }
    }

    private boolean isRetryable(Throwable throwable) {
        return !(throwable instanceof AIServiceException);
    }
}
