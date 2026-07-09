package com.devops.incident.health;

import com.devops.incident.integration.SimulatorClient;
import org.springframework.boot.actuate.health.Health;
import org.springframework.boot.actuate.health.HealthIndicator;
import org.springframework.stereotype.Component;

@Component("simulator")
public class SimulatorHealthIndicator implements HealthIndicator {

    private final SimulatorClient simulatorClient;

    public SimulatorHealthIndicator(SimulatorClient simulatorClient) {
        this.simulatorClient = simulatorClient;
    }

    @Override
    public Health health() {
        return simulatorClient.isAvailable() ? Health.up().build() : Health.down().build();
    }
}
