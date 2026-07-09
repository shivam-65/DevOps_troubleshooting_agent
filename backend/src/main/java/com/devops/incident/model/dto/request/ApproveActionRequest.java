package com.devops.incident.model.dto.request;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class ApproveActionRequest {

    @NotBlank(message = "must not be blank")
    private String approvedBy;
}
