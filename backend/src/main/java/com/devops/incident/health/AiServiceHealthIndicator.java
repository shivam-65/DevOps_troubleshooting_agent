package com.devops.incident.health;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.Duration;

@Component("aiService")
public class AiServiceHealthIndicator implements HealthIndicator {

    private final WebClient webClient;

    public AiServiceHealthIndicator(WebClient.Builder builder,
                                    @Value("${ai-service.base-url:http://localhost:8000}") String baseUrl) {
        this.webClient = builder.baseUrl(baseUrl).build();
    }

    @Override
    public Health health() {
        try {
            webClient.get().uri("/health").retrieve().toBodilessEntity()
                    .timeout(Duration.ofSeconds(3)).block();
            return Health.up().build();
        } catch (Exception e) {
            return Health.down().withDetail("error", e.getMessage()).build();
        }
    }
}
