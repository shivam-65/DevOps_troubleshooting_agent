package com.devops.incident.model.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class WebSocketEvent<T> {
    private String eventType;
    private String entityId;
    private Instant timestamp;
    private T data;

    public static <T> WebSocketEvent<T> of(String eventType, String entityId, T data) {
        return WebSocketEvent.<T>builder()
                .eventType(eventType)
                .entityId(entityId)
                .timestamp(Instant.now())
                .data(data)
                .build();
    }
}
