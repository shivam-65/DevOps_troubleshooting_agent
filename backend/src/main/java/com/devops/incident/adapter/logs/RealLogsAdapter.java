package com.devops.incident.adapter.logs;

import com.devops.incident.adapter.AbstractRealAdapter;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnProperty(name = "adapters.mode", havingValue = "real")
public class RealLogsAdapter extends AbstractRealAdapter {
    @Override
    public String getType() {
        return "logs";
    }
}
