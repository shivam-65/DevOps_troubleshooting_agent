package com.devops.incident.model.enums;

import java.util.EnumSet;
import java.util.Set;

public enum IncidentStatus {
    OPEN,
    INVESTIGATING,
    RESOLVED,
    CLOSED;

    /**
     * Returns the set of statuses this status is allowed to transition to.
     */
    public Set<IncidentStatus> allowedTransitions() {
        return switch (this) {
            case OPEN -> EnumSet.of(INVESTIGATING, CLOSED);
            case INVESTIGATING -> EnumSet.of(RESOLVED, OPEN);
            case RESOLVED -> EnumSet.of(CLOSED, INVESTIGATING);
            case CLOSED -> EnumSet.noneOf(IncidentStatus.class);
        };
    }

    public boolean canTransitionTo(IncidentStatus target) {
        return allowedTransitions().contains(target);
    }
}
