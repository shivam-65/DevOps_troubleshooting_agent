package com.devops.incident.controller;

import com.devops.incident.model.Report;
import com.devops.incident.model.dto.request.GenerateReportRequest;
import com.devops.incident.model.dto.response.PagedResponse;
import com.devops.incident.model.dto.response.ReportResponse;
import com.devops.incident.service.ReportService;
import com.devops.incident.util.PdfUtil;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@Slf4j
@RestController
@RequestMapping("/api/reports")
public class ReportController {

    private final ReportService reportService;

    public ReportController(ReportService reportService) {
        this.reportService = reportService;
    }

    @PostMapping
    public ResponseEntity<ReportResponse> generate(@Valid @RequestBody GenerateReportRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(reportService.generate(request));
    }

    @GetMapping
    public ResponseEntity<PagedResponse<ReportResponse>> list(
            @RequestParam(required = false) String incidentId,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        int cappedSize = Math.min(Math.max(size, 1), 100);
        int safePage = Math.max(page, 0);
        return ResponseEntity.ok(reportService.list(incidentId, safePage, cappedSize));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ReportResponse> get(@PathVariable String id) {
        return ResponseEntity.ok(reportService.getById(id));
    }

    @GetMapping("/{id}/export")
    public ResponseEntity<?> export(@PathVariable String id,
                                    @RequestParam(defaultValue = "JSON") String format) {
        Report report = reportService.getEntity(id);
        if ("PDF".equalsIgnoreCase(format)) {
            byte[] pdf = PdfUtil.textToPdf(report.getTitle(), report.getContent());
            return ResponseEntity.ok()
                    .contentType(MediaType.APPLICATION_PDF)
                    .header(HttpHeaders.CONTENT_DISPOSITION,
                            "attachment; filename=\"report-" + id + ".pdf\"")
                    .body(pdf);
        }
        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_JSON)
                .header(HttpHeaders.CONTENT_DISPOSITION,
                        "attachment; filename=\"report-" + id + ".json\"")
                .body(ReportResponse.from(report));
    }
}
