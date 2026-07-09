package com.devops.incident.service;

import com.devops.incident.exception.ResourceNotFoundException;
import com.devops.incident.model.Action;
import com.devops.incident.model.Incident;
import com.devops.incident.model.Investigation;
import com.devops.incident.model.Report;
import com.devops.incident.model.dto.request.GenerateReportRequest;
import com.devops.incident.model.dto.response.PagedResponse;
import com.devops.incident.model.dto.response.ReportResponse;
import com.devops.incident.model.enums.ActionStatus;
import com.devops.incident.model.enums.ReportFormat;
import com.devops.incident.repository.ActionRepository;
import com.devops.incident.repository.IncidentRepository;
import com.devops.incident.repository.InvestigationRepository;
import com.devops.incident.repository.ReportRepository;
import com.devops.incident.util.JsonUtil;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

@Slf4j
@Service
public class ReportService {

    private final ReportRepository reportRepository;
    private final IncidentRepository incidentRepository;
    private final InvestigationRepository investigationRepository;
    private final ActionRepository actionRepository;

    public ReportService(ReportRepository reportRepository,
                         IncidentRepository incidentRepository,
                         InvestigationRepository investigationRepository,
                         ActionRepository actionRepository) {
        this.reportRepository = reportRepository;
        this.incidentRepository = incidentRepository;
        this.investigationRepository = investigationRepository;
        this.actionRepository = actionRepository;
    }

    public ReportResponse generate(GenerateReportRequest request) {
        Incident incident = incidentRepository.findById(request.getIncidentId())
                .orElseThrow(() -> ResourceNotFoundException.of("Incident", request.getIncidentId()));

        List<Investigation> investigations = investigationRepository.findByIncidentId(incident.getId());
        List<Action> actions = actionRepository.findAll(incident.getId(), null, null, 0, 1000);

        Map<String, Object> content = buildContent(incident, investigations, actions);
        Map<String, Object> metadata = buildMetadata(incident, investigations, actions);

        ReportFormat format = request.getFormat() == null ? ReportFormat.JSON : request.getFormat();
        String title = request.getTitle() != null && !request.getTitle().isBlank()
                ? request.getTitle()
                : "Post-Incident Report: " + incident.getTitle();

        Instant now = Instant.now();
        Report report = Report.builder()
                .id(UUID.randomUUID().toString())
                .incidentId(incident.getId())
                .title(title)
                .content(JsonUtil.toJson(content))
                .format(format)
                .metadata(JsonUtil.toJson(metadata))
                .generatedAt(now)
                .createdAt(now)
                .build();
        reportRepository.save(report);
        log.info("Generated report {} for incident {}", report.getId(), incident.getId());
        return ReportResponse.from(report);
    }

    public ReportResponse getById(String id) {
        return ReportResponse.from(findOrThrow(id));
    }

    public Report getEntity(String id) {
        return findOrThrow(id);
    }

    public PagedResponse<ReportResponse> list(String incidentId, int page, int size) {
        List<ReportResponse> content = reportRepository.findAll(incidentId, page, size).stream()
                .map(ReportResponse::from).toList();
        long total = reportRepository.count(incidentId);
        return PagedResponse.of(content, page, size, total);
    }

    private Map<String, Object> buildContent(Incident incident, List<Investigation> investigations,
                                             List<Action> actions) {
        Map<String, Object> content = new LinkedHashMap<>();
        content.put("incident", Map.of(
                "id", incident.getId(),
                "title", incident.getTitle(),
                "description", incident.getDescription(),
                "severity", incident.getSeverity().name(),
                "status", incident.getStatus().name(),
                "affectedServices", incident.getAffectedServices() == null ? List.of() : incident.getAffectedServices()));
        content.put("investigations", investigations.stream().map(inv -> {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", inv.getId());
            m.put("status", inv.getStatus().name());
            m.put("summary", inv.getSummary());
            m.put("rootCause", inv.getRootCause());
            m.put("confidence", inv.getConfidence());
            return m;
        }).toList());
        content.put("actions", actions.stream().map(a -> {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", a.getId());
            m.put("type", a.getType().name());
            m.put("status", a.getStatus().name());
            m.put("title", a.getTitle());
            return m;
        }).toList());
        return content;
    }

    private Map<String, Object> buildMetadata(Incident incident, List<Investigation> investigations,
                                              List<Action> actions) {
        Map<String, Object> metadata = new LinkedHashMap<>();
        metadata.put("severity", incident.getSeverity().name());
        metadata.put("affectedServices", incident.getAffectedServices() == null ? List.of() : incident.getAffectedServices());

        Instant end = incident.getResolvedAt() != null ? incident.getResolvedAt()
                : (incident.getClosedAt() != null ? incident.getClosedAt() : Instant.now());
        if (incident.getCreatedAt() != null) {
            metadata.put("incidentDuration", Duration.between(incident.getCreatedAt(), end).toString());
        }
        String rootCause = investigations.stream()
                .map(Investigation::getRootCause)
                .filter(rc -> rc != null && !rc.isBlank())
                .findFirst().orElse(null);
        metadata.put("rootCause", rootCause);
        long executed = actions.stream().filter(a -> a.getStatus() == ActionStatus.COMPLETED).count();
        metadata.put("actionsExecuted", executed);
        metadata.put("actionsProposed", actions.size());
        return metadata;
    }

    private Report findOrThrow(String id) {
        return reportRepository.findById(id)
                .orElseThrow(() -> ResourceNotFoundException.of("Report", id));
    }
}
