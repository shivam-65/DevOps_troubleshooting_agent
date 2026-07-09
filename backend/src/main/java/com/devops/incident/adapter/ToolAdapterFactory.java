package com.devops.incident.adapter;

import com.devops.incident.exception.AdapterException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

@Slf4j
@Component
public class ToolAdapterFactory {

    private final Map<String, ToolAdapter> adapters;

    public ToolAdapterFactory(List<ToolAdapter> adapterList) {
        this.adapters = adapterList.stream()
                .collect(Collectors.toMap(ToolAdapter::getType, Function.identity(), (a, b) -> a));
        log.info("Registered tool adapters: {}", adapters.keySet());
    }

    public ToolAdapter getAdapter(String type) {
        ToolAdapter adapter = adapters.get(type);
        if (adapter == null) {
            throw new AdapterException("No adapter registered for type: " + type);
        }
        return adapter;
    }

    public boolean hasAdapter(String type) {
        return adapters.containsKey(type);
    }
}
