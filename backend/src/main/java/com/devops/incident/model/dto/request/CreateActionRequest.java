package com.devops.incident.model.dto.request;

import com.devops.incident.model.enums.ActionType;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.util.Map;

@Data
public class CreateActionRequest {

    @NotBlank(message = "must not be blank")
    private String investigationId;

    @NotBlank(message = "must not be blank")
    private String incidentId;

    @NotNull(message = "must be a valid action type")
    private ActionType type;

    @NotBlank(message = "must not be blank")
    @Size(max = 255, message = "must not exceed 255 characters")
    private String title;

    @Size(max = 5000, message = "must not exceed 5000 characters")
    private String description;

    @Size(max = 2000, message = "must not exceed 2000 characters")
    private String command;

    @Size(max = 100, message = "must not exceed 100 characters")
    private String targetService;

    private Map<String, Object> parameters;

    @Size(max = 50, message = "must not exceed 50 characters")
    private String risk;

    @Size(max = 500, message = "must not exceed 500 characters")
    private String estimatedImpact;
}
