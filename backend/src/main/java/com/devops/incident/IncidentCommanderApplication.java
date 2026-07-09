package com.devops.incident;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableAsync
public class IncidentCommanderApplication {

    public static void main(String[] args) {
        SpringApplication.run(IncidentCommanderApplication.class, args);
    }
}
