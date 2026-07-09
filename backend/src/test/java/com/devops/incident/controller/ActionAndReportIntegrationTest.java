package com.devops.incident.controller;

import com.devops.incident.model.dto.request.ApproveActionRequest;
import com.devops.incident.model.dto.request.CreateActionRequest;
import com.devops.incident.model.dto.request.CreateIncidentRequest;
import com.devops.incident.model.dto.request.GenerateReportRequest;
import com.devops.incident.model.dto.response.ActionResponse;
import com.devops.incident.model.dto.response.IncidentResponse;
import com.devops.incident.model.dto.response.InvestigationResponse;
import com.devops.incident.model.dto.response.ReportResponse;
import com.devops.incident.model.enums.ActionStatus;
import com.devops.incident.model.enums.ActionType;
import com.devops.incident.model.enums.IncidentSeverity;
import com.devops.incident.model.enums.ReportFormat;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class ActionAndReportIntegrationTest {

    @Autowired
    private TestRestTemplate restTemplate;

    private String createIncident() {
        CreateIncidentRequest req = new CreateIncidentRequest();
        req.setTitle("OOM in payment-api");
        req.setDescription("Pods crashing with OOMKilled");
        req.setSeverity(IncidentSeverity.CRITICAL);
        req.setAffectedServices(List.of("payment-api"));
        return restTemplate.postForEntity("/api/incidents", req, IncidentResponse.class).getBody().getId();
    }

    private String triggerInvestigation(String incidentId) {
        ResponseEntity<InvestigationResponse> response = restTemplate.postForEntity(
                "/api/incidents/" + incidentId + "/investigations",
                new com.devops.incident.model.dto.request.TriggerInvestigationRequest(),
                InvestigationResponse.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.ACCEPTED);
        return response.getBody().getId();
    }

    @Test
    void shouldCreateApproveAction() {
        String incidentId = createIncident();
        String investigationId = triggerInvestigation(incidentId);

        CreateActionRequest req = new CreateActionRequest();
        req.setIncidentId(incidentId);
        req.setInvestigationId(investigationId);
        req.setType(ActionType.RESTART_SERVICE);
        req.setTitle("Restart payment-api pods");
        req.setTargetService("payment-api");
        req.setRisk("MEDIUM");

        ResponseEntity<ActionResponse> created = restTemplate.postForEntity(
                "/api/actions", req, ActionResponse.class);
        assertThat(created.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(created.getBody().getStatus()).isEqualTo(ActionStatus.PROPOSED);
        String actionId = created.getBody().getId();

        ApproveActionRequest approve = new ApproveActionRequest();
        approve.setApprovedBy("jane.doe");
        ResponseEntity<ActionResponse> approved = restTemplate.postForEntity(
                "/api/actions/" + actionId + "/approve", approve, ActionResponse.class);
        assertThat(approved.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(approved.getBody().getStatus()).isEqualTo(ActionStatus.APPROVED);
    }

    @Test
    void shouldRejectActionCreationForUnknownInvestigation() {
        String incidentId = createIncident();
        CreateActionRequest req = new CreateActionRequest();
        req.setIncidentId(incidentId);
        req.setInvestigationId("missing-investigation");
        req.setType(ActionType.SCALE_UP);
        req.setTitle("Scale up");

        ResponseEntity<String> response = restTemplate.postForEntity("/api/actions", req, String.class);
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.NOT_FOUND);
    }

    @Test
    void shouldGenerateAndExportReport() {
        String incidentId = createIncident();

        GenerateReportRequest req = new GenerateReportRequest();
        req.setIncidentId(incidentId);
        req.setTitle("Post-Incident Report");
        req.setFormat(ReportFormat.JSON);

        ResponseEntity<ReportResponse> created = restTemplate.postForEntity(
                "/api/reports", req, ReportResponse.class);
        assertThat(created.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        String reportId = created.getBody().getId();
        assertThat(created.getBody().getContent()).isNotBlank();

        // Export JSON
        ResponseEntity<String> jsonExport = restTemplate.getForEntity(
                "/api/reports/" + reportId + "/export?format=JSON", String.class);
        assertThat(jsonExport.getStatusCode()).isEqualTo(HttpStatus.OK);

        // Export PDF
        ResponseEntity<byte[]> pdfExport = restTemplate.getForEntity(
                "/api/reports/" + reportId + "/export?format=PDF", byte[].class);
        assertThat(pdfExport.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(pdfExport.getHeaders().getContentType()).isEqualTo(MediaType.APPLICATION_PDF);
        assertThat(pdfExport.getBody()).isNotEmpty();
        // valid PDF header
        String header = new String(pdfExport.getBody(), 0, 5);
        assertThat(header).isEqualTo("%PDF-");
    }
}
