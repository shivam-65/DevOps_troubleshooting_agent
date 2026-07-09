package com.devops.incident.controller;

import com.devops.incident.model.dto.request.CreateIncidentRequest;
import com.devops.incident.model.dto.response.IncidentResponse;
import com.devops.incident.model.dto.response.InvestigationResponse;
import com.devops.incident.model.enums.IncidentSeverity;
import com.devops.incident.model.enums.InvestigationStatus;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.awaitility.Awaitility.await;

import java.time.Duration;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class InvestigationCallbackIntegrationTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void shouldProcessAiCallbackAndPopulateInvestigation() {
        CreateIncidentRequest req = new CreateIncidentRequest();
        req.setTitle("Latency spike");
        req.setDescription("High latency on payment-api");
        req.setSeverity(IncidentSeverity.HIGH);
        req.setAffectedServices(List.of("payment-api"));
        String incidentId = restTemplate.postForEntity("/api/incidents", req, IncidentResponse.class)
                .getBody().getId();

        String investigationId = restTemplate.postForEntity(
                "/api/incidents/" + incidentId + "/investigations",
                new com.devops.incident.model.dto.request.TriggerInvestigationRequest(),
                InvestigationResponse.class)
                .getBody().getId();

        // Wait for the async AI trigger to settle (it fails fast against the unused port in tests).
        await().atMost(Duration.ofSeconds(5)).untilAsserted(() -> {
            ResponseEntity<InvestigationResponse> r = restTemplate.getForEntity(
                    "/api/incidents/" + incidentId + "/investigations/" + investigationId,
                    InvestigationResponse.class);
            assertThat(r.getBody().getStatus()).isEqualTo(InvestigationStatus.FAILED);
        });

        // Now deliver the AI callback; this should override the state to COMPLETED.
        Map<String, Object> callback = Map.of(
                "investigationId", investigationId,
                "status", "COMPLETED",
                "summary", "Memory leak detected",
                "rootCause", "Unclosed DB connections",
                "confidence", 0.91,
                "aiModelUsed", "gemini-1.5",
                "evidence", List.of(Map.of(
                        "source", "logs",
                        "type", "error_log",
                        "data", Map.of("entries", List.of("OutOfMemoryError")))),
                "recommendedActions", List.of(Map.of(
                        "type", "RESTART_SERVICE",
                        "title", "Restart payment-api",
                        "targetService", "payment-api",
                        "risk", "MEDIUM",
                        "estimatedImpact", "~30s downtime")));

        ResponseEntity<InvestigationResponse> callbackResponse = restTemplate.postForEntity(
                "/api/internal/investigations/" + investigationId + "/callback",
                callback, InvestigationResponse.class);
        assertThat(callbackResponse.getStatusCode()).isEqualTo(HttpStatus.OK);

        ResponseEntity<InvestigationResponse> finalState = restTemplate.getForEntity(
                "/api/incidents/" + incidentId + "/investigations/" + investigationId,
                InvestigationResponse.class);
        InvestigationResponse body = finalState.getBody();
        assertThat(body.getStatus()).isEqualTo(InvestigationStatus.COMPLETED);
        assertThat(body.getRootCause()).isEqualTo("Unclosed DB connections");
        assertThat(body.getConfidence()).isEqualTo(0.91);
        assertThat(body.getEvidence()).hasSize(1);
        assertThat(body.getActions()).hasSize(1);
    }
}
