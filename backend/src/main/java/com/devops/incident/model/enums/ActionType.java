package com.devops.incident.model.enums;

public enum ActionType {
    RESTART_SERVICE,
    SCALE_UP,
    ROLLBACK_DEPLOYMENT,
    RUN_SCRIPT,
    APPLY_CONFIG_CHANGE,
    CLEAR_CACHE,
    FAILOVER,
    CUSTOM
}
