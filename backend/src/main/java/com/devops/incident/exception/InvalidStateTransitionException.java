package com.devops.incident.exception;

import lombok.Getter;

import java.util.Map;

@Getter
public class InvalidStateTransitionException extends RuntimeException {

    private final transient Map<String, Object> details;

    public InvalidStateTransitionException(String message) {
        super(message);
        this.details = null;
    }

    public InvalidStateTransitionException(String message, Map<String, Object> details) {
        super(message);
        this.details = details;
    }
}
