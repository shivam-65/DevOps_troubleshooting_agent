package com.devops.incident.websocket;

import lombok.extern.slf4j.Slf4j;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.messaging.SessionConnectedEvent;
import org.springframework.web.socket.messaging.SessionDisconnectEvent;
import org.springframework.web.socket.messaging.SessionSubscribeEvent;

/**
 * Logs STOMP WebSocket lifecycle events. Event broadcasting itself is handled by
 * {@link com.devops.incident.service.EventPublisherService} via SimpMessagingTemplate.
 */
@Slf4j
@Component
public class WebSocketEventHandler {

    @EventListener
    public void onConnect(SessionConnectedEvent event) {
        log.debug("WebSocket client connected: {}", event.getMessage().getHeaders().get("simpSessionId"));
    }

    @EventListener
    public void onSubscribe(SessionSubscribeEvent event) {
        Object destination = event.getMessage().getHeaders().get("simpDestination");
        log.debug("WebSocket subscription to {}", destination);
    }

    @EventListener
    public void onDisconnect(SessionDisconnectEvent event) {
        log.debug("WebSocket client disconnected: {}", event.getSessionId());
    }
}
