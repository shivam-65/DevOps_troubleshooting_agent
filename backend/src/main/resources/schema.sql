-- ============================================================
-- INCIDENTS
-- ============================================================
CREATE TABLE IF NOT EXISTS incidents (
    id                VARCHAR(36)   PRIMARY KEY,
    title             VARCHAR(255)  NOT NULL,
    description       VARCHAR(5000) NOT NULL,
    severity          VARCHAR(20)   NOT NULL,
    status            VARCHAR(20)   NOT NULL DEFAULT 'OPEN',
    affected_services CLOB,
    assignee          VARCHAR(100),
    tags              CLOB,
    created_at        TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at       TIMESTAMP,
    closed_at         TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_incidents_status   ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);
CREATE INDEX IF NOT EXISTS idx_incidents_created  ON incidents(created_at);

-- ============================================================
-- INVESTIGATIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS investigations (
    id              VARCHAR(36)   PRIMARY KEY,
    incident_id     VARCHAR(36)   NOT NULL,
    status          VARCHAR(20)   NOT NULL DEFAULT 'PENDING',
    summary         VARCHAR(5000),
    root_cause      VARCHAR(5000),
    confidence      DOUBLE,
    ai_model_used   VARCHAR(100),
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP,
    created_at      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_investigations_incident ON investigations(incident_id);
CREATE INDEX IF NOT EXISTS idx_investigations_status   ON investigations(status);

-- ============================================================
-- INVESTIGATION EVIDENCE
-- ============================================================
CREATE TABLE IF NOT EXISTS investigation_evidence (
    id                VARCHAR(36)   PRIMARY KEY,
    investigation_id  VARCHAR(36)   NOT NULL,
    source            VARCHAR(100)  NOT NULL,
    type              VARCHAR(100)  NOT NULL,
    data              CLOB          NOT NULL,
    collected_at      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (investigation_id) REFERENCES investigations(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_evidence_investigation ON investigation_evidence(investigation_id);

-- ============================================================
-- ACTIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS actions (
    id                VARCHAR(36)   PRIMARY KEY,
    investigation_id  VARCHAR(36)   NOT NULL,
    incident_id       VARCHAR(36)   NOT NULL,
    type              VARCHAR(30)   NOT NULL,
    status            VARCHAR(20)   NOT NULL DEFAULT 'PROPOSED',
    title             VARCHAR(255)  NOT NULL,
    description       VARCHAR(5000),
    command           VARCHAR(2000),
    target_service    VARCHAR(100),
    parameters        CLOB,
    risk              VARCHAR(50),
    estimated_impact  VARCHAR(500),
    execution_result  CLOB,
    approved_by       VARCHAR(100),
    approved_at       TIMESTAMP,
    executed_at       TIMESTAMP,
    completed_at      TIMESTAMP,
    created_at        TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (investigation_id) REFERENCES investigations(id) ON DELETE CASCADE,
    FOREIGN KEY (incident_id)      REFERENCES incidents(id)      ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_actions_investigation ON actions(investigation_id);
CREATE INDEX IF NOT EXISTS idx_actions_incident      ON actions(incident_id);
CREATE INDEX IF NOT EXISTS idx_actions_status        ON actions(status);

-- ============================================================
-- REPORTS
-- ============================================================
CREATE TABLE IF NOT EXISTS reports (
    id            VARCHAR(36)   PRIMARY KEY,
    incident_id   VARCHAR(36)   NOT NULL,
    title         VARCHAR(255)  NOT NULL,
    content       CLOB          NOT NULL,
    format        VARCHAR(10)   NOT NULL DEFAULT 'JSON',
    metadata      CLOB,
    generated_at  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_reports_incident ON reports(incident_id);
