package com.devops.incident.service;

import com.devops.incident.model.dto.response.WebSocketEvent;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

@Slf4j
@Service
public class EventPublisherService {

    private final SimpMessagingTemplate messagingTemplate;

    public EventPublisherService(SimpMessagingTemplate messagingTemplate) {
        this.messagingTemplate = messagingTemplate;
    }

    public <T> void publish(String topic, String eventType, String entityId, T data) {
        WebSocketEvent<T> event = WebSocketEvent.of(eventType, entityId, data);
        log.debug("Publishing {} event for {} to {}", eventType, entityId, topic);
        try {
            messagingTemplate.convertAndSend(topic, event);
        } catch (Exception e) {
            log.warn("Failed to publish WebSocket event {} to {}: {}", eventType, topic, e.getMessage());
        }
    }

    public <T> void publishIncidentEvent(String eventType, String incidentId, T data) {
        publish("/topic/incidents", eventType, incidentId, data);
    }

    public <T> void publishInvestigationEvent(String eventType, String incidentId, String investigationId, T data) {
        publish("/topic/incidents/" + incidentId + "/investigations", eventType, investigationId, data);
    }

    public <T> void publishActionEvent(String eventType, String actionId, T data) {
        publish("/topic/actions", eventType, actionId, data);
    }
}
