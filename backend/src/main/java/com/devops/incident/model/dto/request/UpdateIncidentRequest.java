package com.devops.incident.model.dto.request;

import com.devops.incident.model.enums.IncidentSeverity;
import com.devops.incident.model.enums.IncidentStatus;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.util.List;

@Data
public class UpdateIncidentRequest {

    @Size(max = 255, message = "must not exceed 255 characters")
    private String title;

    @Size(max = 5000, message = "must not exceed 5000 characters")
    private String description;

    private IncidentSeverity severity;

    private IncidentStatus status;

    private List<String> affectedServices;

    @Size(max = 100, message = "must not exceed 100 characters")
    private String assignee;

    private List<String> tags;
}
