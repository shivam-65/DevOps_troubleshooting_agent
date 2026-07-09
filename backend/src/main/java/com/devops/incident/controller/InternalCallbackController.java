package com.devops.incident.controller;

import com.devops.incident.integration.dto.AIAnalysisResult;
import com.devops.incident.model.dto.response.InvestigationResponse;
import com.devops.incident.service.InvestigationService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/api/internal/investigations")
public class InternalCallbackController {

    private final InvestigationService investigationService;

    public InternalCallbackController(InvestigationService investigationService) {
        this.investigationService = investigationService;
    }

    @PostMapping("/{investigationId}/callback")
    public ResponseEntity<InvestigationResponse> callback(@PathVariable String investigationId,
                                                          @RequestBody AIAnalysisResult result) {
        log.info("AI callback received for investigation {} (status={})", investigationId, result.getStatus());
        return ResponseEntity.ok(investigationService.processCallback(investigationId, result));
    }
}
