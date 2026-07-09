package com.devops.incident.service;

import com.devops.incident.exception.InvalidStateTransitionException;
import com.devops.incident.exception.ResourceNotFoundException;
import com.devops.incident.model.Incident;
import com.devops.incident.model.dto.request.CreateIncidentRequest;
import com.devops.incident.model.dto.request.UpdateIncidentRequest;
import com.devops.incident.model.dto.response.IncidentResponse;
import com.devops.incident.model.dto.response.PagedResponse;
import com.devops.incident.model.enums.IncidentSeverity;
import com.devops.incident.model.enums.IncidentStatus;
import com.devops.incident.repository.IncidentRepository;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Slf4j
@Service
public class IncidentService {

    private final IncidentRepository incidentRepository;
    private final EventPublisherService eventPublisher;

    public IncidentService(IncidentRepository incidentRepository, EventPublisherService eventPublisher) {
        this.incidentRepository = incidentRepository;
        this.eventPublisher = eventPublisher;
    }

    public IncidentResponse create(CreateIncidentRequest request) {
        Instant now = Instant.now();
        Incident incident = Incident.builder()
                .id(UUID.randomUUID().toString())
                .title(request.getTitle())
                .description(request.getDescription())
                .severity(request.getSeverity())
                .status(IncidentStatus.OPEN)
                .affectedServices(request.getAffectedServices())
                .assignee(request.getAssignee())
                .tags(request.getTags())
                .createdAt(now)
                .updatedAt(now)
                .build();
        incidentRepository.save(incident);
        log.info("Created incident {} ({})", incident.getId(), incident.getTitle());
        IncidentResponse response = IncidentResponse.from(incident);
        eventPublisher.publishIncidentEvent("INCIDENT_CREATED", incident.getId(), response);
        return response;
    }

    public IncidentResponse getById(String id) {
        return IncidentResponse.from(findOrThrow(id));
    }

    public Incident getEntity(String id) {
        return findOrThrow(id);
    }

    public PagedResponse<IncidentResponse> list(IncidentStatus status, IncidentSeverity severity, String search,
                                                String sortBy, String sortDir, int page, int size) {
        List<IncidentResponse> content = incidentRepository
                .findAll(status, severity, search, sortBy, sortDir, page, size)
                .stream().map(IncidentResponse::from).toList();
        long total = incidentRepository.count(status, severity, search);
        return PagedResponse.of(content, page, size, total);
    }

    public IncidentResponse update(String id, UpdateIncidentRequest request) {
        Incident incident = findOrThrow(id);

        if (request.getTitle() != null) {
            incident.setTitle(request.getTitle());
        }
        if (request.getDescription() != null) {
            incident.setDescription(request.getDescription());
        }
        if (request.getSeverity() != null) {
            incident.setSeverity(request.getSeverity());
        }
        if (request.getAffectedServices() != null) {
            incident.setAffectedServices(request.getAffectedServices());
        }
        if (request.getAssignee() != null) {
            incident.setAssignee(request.getAssignee());
        }
        if (request.getTags() != null) {
            incident.setTags(request.getTags());
        }
        if (request.getStatus() != null && request.getStatus() != incident.getStatus()) {
            applyStatusTransition(incident, request.getStatus());
        }

        incident.setUpdatedAt(Instant.now());
        incidentRepository.update(incident);
        log.info("Updated incident {}", id);
        IncidentResponse response = IncidentResponse.from(incident);
        eventPublisher.publishIncidentEvent("INCIDENT_UPDATED", id, response);
        return response;
    }

    /**
     * Transitions an incident's status, validating the lifecycle rules.
     */
    public IncidentResponse updateStatus(String id, IncidentStatus target) {
        Incident incident = findOrThrow(id);
        applyStatusTransition(incident, target);
        incident.setUpdatedAt(Instant.now());
        incidentRepository.update(incident);
        IncidentResponse response = IncidentResponse.from(incident);
        eventPublisher.publishIncidentEvent("INCIDENT_UPDATED", id, response);
        return response;
    }

    private void applyStatusTransition(Incident incident, IncidentStatus target) {
        IncidentStatus current = incident.getStatus();
        if (current == target) {
            return;
        }
        if (!current.canTransitionTo(target)) {
            throw new InvalidStateTransitionException(
                    "Invalid state transition: cannot move from " + current + " to " + target,
                    Map.of(
                            "field", "status",
                            "currentValue", current.name(),
                            "requestedValue", target.name(),
                            "allowedValues", current.allowedTransitions().stream().map(Enum::name).toList()));
        }
        incident.setStatus(target);
        Instant now = Instant.now();
        if (target == IncidentStatus.RESOLVED) {
            incident.setResolvedAt(now);
        } else if (target == IncidentStatus.CLOSED) {
            incident.setClosedAt(now);
        }
        log.info("Incident {} transitioned {} -> {}", incident.getId(), current, target);
    }

    public void delete(String id) {
        Incident incident = findOrThrow(id);
        incidentRepository.deleteById(id);
        log.info("Deleted incident {}", id);
        eventPublisher.publishIncidentEvent("INCIDENT_DELETED", id, IncidentResponse.from(incident));
    }

    private Incident findOrThrow(String id) {
        return incidentRepository.findById(id)
                .orElseThrow(() -> ResourceNotFoundException.of("Incident", id));
    }
}
