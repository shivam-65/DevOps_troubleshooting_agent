package com.devops.incident.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI incidentCommanderOpenAPI() {
        return new OpenAPI().info(new Info()
                .title("AI-Powered DevOps Incident Commander API")
                .description("Backend REST API for incident management, AI investigation, remediation, and reporting.")
                .version("v1"));
    }
}
