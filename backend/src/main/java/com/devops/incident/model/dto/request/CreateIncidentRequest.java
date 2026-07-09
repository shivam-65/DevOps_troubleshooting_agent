package com.devops.incident.model.dto.request;

import com.devops.incident.model.enums.IncidentSeverity;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.util.List;

@Data
public class CreateIncidentRequest {

    @NotBlank(message = "must not be blank")
    @Size(max = 255, message = "must not exceed 255 characters")
    private String title;

    @NotBlank(message = "must not be blank")
    @Size(max = 5000, message = "must not exceed 5000 characters")
    private String description;

    @NotNull(message = "must be one of: CRITICAL, HIGH, MEDIUM, LOW")
    private IncidentSeverity severity;

    private List<String> affectedServices;

    @Size(max = 100, message = "must not exceed 100 characters")
    private String assignee;

    private List<String> tags;
}
