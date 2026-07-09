package com.devops.incident.controller;

import com.devops.incident.model.dto.request.CreateIncidentRequest;
import com.devops.incident.model.dto.request.UpdateIncidentRequest;
import com.devops.incident.model.dto.response.IncidentResponse;
import com.devops.incident.model.dto.response.PagedResponse;
import com.devops.incident.model.enums.IncidentSeverity;
import com.devops.incident.model.enums.IncidentStatus;
import com.devops.incident.service.IncidentService;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/api/incidents")
public class IncidentController {

    private final IncidentService incidentService;

    public IncidentController(IncidentService incidentService) {
        this.incidentService = incidentService;
    }

    @PostMapping
    public ResponseEntity<IncidentResponse> create(@Valid @RequestBody CreateIncidentRequest request) {
        log.info("POST /api/incidents");
        return ResponseEntity.status(HttpStatus.CREATED).body(incidentService.create(request));
    }

    @GetMapping
    public ResponseEntity<PagedResponse<IncidentResponse>> list(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(required = false) IncidentStatus status,
            @RequestParam(required = false) IncidentSeverity severity,
            @RequestParam(required = false) String search,
            @RequestParam(defaultValue = "createdAt") String sortBy,
            @RequestParam(defaultValue = "desc") String sortDir) {
        int cappedSize = Math.min(Math.max(size, 1), 100);
        int safePage = Math.max(page, 0);
        return ResponseEntity.ok(
                incidentService.list(status, severity, search, sortBy, sortDir, safePage, cappedSize));
    }

    @GetMapping("/{id}")
    public ResponseEntity<IncidentResponse> get(@PathVariable String id) {
        return ResponseEntity.ok(incidentService.getById(id));
    }

    @PutMapping("/{id}")
    public ResponseEntity<IncidentResponse> update(@PathVariable String id,
                                                   @Valid @RequestBody UpdateIncidentRequest request) {
        return ResponseEntity.ok(incidentService.update(id, request));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable String id) {
        incidentService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
