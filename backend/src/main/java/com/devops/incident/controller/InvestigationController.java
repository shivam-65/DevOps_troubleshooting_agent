package com.devops.incident.controller;

import com.devops.incident.model.dto.request.TriggerInvestigationRequest;
import com.devops.incident.model.dto.response.EvidenceResponse;
import com.devops.incident.model.dto.response.InvestigationResponse;
import com.devops.incident.service.InvestigationService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/incidents/{incidentId}/investigations")
public class InvestigationController {

    private final InvestigationService investigationService;

    public InvestigationController(InvestigationService investigationService) {
        this.investigationService = investigationService;
    }

    @PostMapping
    public ResponseEntity<InvestigationResponse> trigger(
            @PathVariable String incidentId,
            @RequestBody(required = false) TriggerInvestigationRequest request) {
        log.info("POST /api/incidents/{}/investigations", incidentId);
        return ResponseEntity.status(HttpStatus.ACCEPTED)
                .body(investigationService.trigger(incidentId, request));
    }

    @GetMapping
    public ResponseEntity<List<InvestigationResponse>> list(@PathVariable String incidentId) {
        return ResponseEntity.ok(investigationService.listByIncident(incidentId));
    }

    @GetMapping("/{investigationId}")
    public ResponseEntity<InvestigationResponse> get(@PathVariable String incidentId,
                                                     @PathVariable String investigationId) {
        return ResponseEntity.ok(investigationService.getDetailed(incidentId, investigationId));
    }

    @GetMapping("/{investigationId}/evidence")
    public ResponseEntity<List<EvidenceResponse>> evidence(@PathVariable String incidentId,
                                                           @PathVariable String investigationId) {
        return ResponseEntity.ok(investigationService.getEvidence(incidentId, investigationId));
    }
}
