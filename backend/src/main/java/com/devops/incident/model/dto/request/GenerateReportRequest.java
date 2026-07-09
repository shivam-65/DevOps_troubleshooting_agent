package com.devops.incident.model.dto.request;

import com.devops.incident.model.enums.ReportFormat;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class GenerateReportRequest {

    @NotBlank(message = "must not be blank")
    private String incidentId;

    @Size(max = 255, message = "must not exceed 255 characters")
    private String title;

    private ReportFormat format;
}
