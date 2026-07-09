package com.devops.incident.controller;

import com.devops.incident.model.dto.request.ApproveActionRequest;
import com.devops.incident.model.dto.request.CreateActionRequest;
import com.devops.incident.model.dto.request.RejectActionRequest;
import com.devops.incident.model.dto.response.ActionResponse;
import com.devops.incident.model.dto.response.PagedResponse;
import com.devops.incident.model.enums.ActionStatus;
import com.devops.incident.service.ActionService;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/api/actions")
public class ActionController {

    private final ActionService actionService;

    public ActionController(ActionService actionService) {
        this.actionService = actionService;
    }

    @PostMapping
    public ResponseEntity<ActionResponse> create(@Valid @RequestBody CreateActionRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(actionService.create(request));
    }

    @GetMapping
    public ResponseEntity<PagedResponse<ActionResponse>> list(
            @RequestParam(required = false) String incidentId,
            @RequestParam(required = false) String investigationId,
            @RequestParam(required = false) ActionStatus status,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        int cappedSize = Math.min(Math.max(size, 1), 100);
        int safePage = Math.max(page, 0);
        return ResponseEntity.ok(actionService.list(incidentId, investigationId, status, safePage, cappedSize));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ActionResponse> get(@PathVariable String id) {
        return ResponseEntity.ok(actionService.getById(id));
    }

    @PostMapping("/{id}/approve")
    public ResponseEntity<ActionResponse> approve(@PathVariable String id,
                                                  @Valid @RequestBody ApproveActionRequest request) {
        return ResponseEntity.ok(actionService.approve(id, request));
    }

    @PostMapping("/{id}/reject")
    public ResponseEntity<ActionResponse> reject(@PathVariable String id,
                                                 @RequestBody(required = false) RejectActionRequest request) {
        return ResponseEntity.ok(actionService.reject(id, request));
    }

    @PostMapping("/{id}/execute")
    public ResponseEntity<ActionResponse> execute(@PathVariable String id) {
        return ResponseEntity.status(HttpStatus.ACCEPTED).body(actionService.execute(id));
    }
}
