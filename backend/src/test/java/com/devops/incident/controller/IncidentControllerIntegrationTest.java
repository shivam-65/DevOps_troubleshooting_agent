package com.devops.incident.controller;

import com.devops.incident.model.dto.request.CreateIncidentRequest;
import com.devops.incident.model.dto.request.UpdateIncidentRequest;
import com.devops.incident.model.dto.response.IncidentResponse;
import com.devops.incident.model.enums.IncidentSeverity;
import com.devops.incident.model.enums.IncidentStatus;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class IncidentControllerIntegrationTest {

    @Autowired
    private TestRestTemplate restTemplate;

    private CreateIncidentRequest sampleRequest() {
        CreateIncidentRequest req = new CreateIncidentRequest();
        req.setTitle("Payment service latency spike");
        req.setDescription("Payment service experiencing 5x latency increase");
        req.setSeverity(IncidentSeverity.HIGH);
        req.setAffectedServices(List.of("payment-api", "checkout-service"));
        req.setAssignee("john.doe");
        req.setTags(List.of("payment", "latency"));
        return req;
    }

    @Test
    void shouldCreateAndRetrieveIncident() {
        ResponseEntity<IncidentResponse> created = restTemplate.postForEntity(
                "/api/incidents", sampleRequest(), IncidentResponse.class);

        assertThat(created.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        IncidentResponse body = created.getBody();
        assertThat(body).isNotNull();
        assertThat(body.getId()).isNotBlank();
        assertThat(body.getStatus()).isEqualTo(IncidentStatus.OPEN);
        assertThat(body.getAffectedServices()).containsExactly("payment-api", "checkout-service");

        ResponseEntity<IncidentResponse> fetched = restTemplate.getForEntity(
                "/api/incidents/" + body.getId(), IncidentResponse.class);
        assertThat(fetched.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(fetched.getBody().getTitle()).isEqualTo("Payment service latency spike");
    }

    @Test
    void shouldReturn404ForUnknownIncident() {
        ResponseEntity<String> response = restTemplate.getForEntity(
                "/api/incidents/does-not-exist", String.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }

    @Test
    void shouldReturn400ForInvalidRequest() {
        CreateIncidentRequest req = new CreateIncidentRequest();
        req.setTitle("");  // blank
        req.setDescription("");  // blank
        ResponseEntity<String> response = restTemplate.postForEntity(
                "/api/incidents", req, String.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
    }

    @Test
    void shouldUpdateStatusWithValidTransition() {
        IncidentResponse created = restTemplate.postForEntity(
                "/api/incidents", sampleRequest(), IncidentResponse.class).getBody();

        UpdateIncidentRequest update = new UpdateIncidentRequest();
        update.setStatus(IncidentStatus.INVESTIGATING);

        ResponseEntity<IncidentResponse> updated = restTemplate.exchange(
                "/api/incidents/" + created.getId(),
                org.springframework.http.HttpMethod.PUT,
                new org.springframework.http.HttpEntity<>(update),
                IncidentResponse.class);

        assertThat(updated.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(updated.getBody().getStatus()).isEqualTo(IncidentStatus.INVESTIGATING);
    }

    @Test
    void shouldRejectInvalidStatusTransition() {
        IncidentResponse created = restTemplate.postForEntity(
                "/api/incidents", sampleRequest(), IncidentResponse.class).getBody();

        // Move to CLOSED directly (OPEN -> CLOSED allowed), then attempt CLOSED -> INVESTIGATING (invalid)
        UpdateIncidentRequest close = new UpdateIncidentRequest();
        close.setStatus(IncidentStatus.CLOSED);
        restTemplate.exchange("/api/incidents/" + created.getId(),
                org.springframework.http.HttpMethod.PUT,
                new org.springframework.http.HttpEntity<>(close), IncidentResponse.class);

        UpdateIncidentRequest invalid = new UpdateIncidentRequest();
        invalid.setStatus(IncidentStatus.INVESTIGATING);
        ResponseEntity<String> response = restTemplate.exchange(
                "/api/incidents/" + created.getId(),
                org.springframework.http.HttpMethod.PUT,
                new org.springframework.http.HttpEntity<>(invalid), String.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.BAD_REQUEST);
    }

    @Test
    void shouldDeleteIncident() {
        IncidentResponse created = restTemplate.postForEntity(
                "/api/incidents", sampleRequest(), IncidentResponse.class).getBody();

        restTemplate.delete("/api/incidents/" + created.getId());

        ResponseEntity<String> fetched = restTemplate.getForEntity(
                "/api/incidents/" + created.getId(), String.class);
        assertThat(fetched.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }

    @Test
    void shouldListIncidents() {
        restTemplate.postForEntity("/api/incidents", sampleRequest(), IncidentResponse.class);
        ResponseEntity<String> response = restTemplate.getForEntity(
                "/api/incidents?page=0&size=10", String.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).contains("totalElements");
    }
}
