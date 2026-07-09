package com.devops.incident.adapter.metrics;

import com.devops.incident.adapter.AbstractSimulatedAdapter;
import com.devops.incident.integration.SimulatorClient;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnProperty(name = "adapters.mode", havingValue = "simulator", matchIfMissing = true)
public class SimulatedMetricsAdapter extends AbstractSimulatedAdapter {

    public SimulatedMetricsAdapter(SimulatorClient simulatorClient) {
        super(simulatorClient);
    }

    @Override
    public String getType() {
        return "metrics";
    }
}
