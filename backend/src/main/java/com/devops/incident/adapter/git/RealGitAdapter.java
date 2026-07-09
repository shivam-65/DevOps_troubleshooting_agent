package com.devops.incident.adapter.git;

import com.devops.incident.adapter.AbstractRealAdapter;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnProperty(name = "adapters.mode", havingValue = "real")
public class RealGitAdapter extends AbstractRealAdapter {
    @Override
    public String getType() {
        return "git";
    }
}
