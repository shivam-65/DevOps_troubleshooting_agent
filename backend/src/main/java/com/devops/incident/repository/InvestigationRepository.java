package com.devops.incident.repository;

import com.devops.incident.model.Investigation;
import com.devops.incident.model.enums.InvestigationStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;

import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.Optional;

@Repository
public class InvestigationRepository {

    private final JdbcTemplate jdbc;

    public InvestigationRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    private final RowMapper<Investigation> mapper = (rs, rowNum) -> {
        Double confidence = rs.getObject("confidence") == null ? null : rs.getDouble("confidence");
        return Investigation.builder()
                .id(rs.getString("id"))
                .incidentId(rs.getString("incident_id"))
                .status(InvestigationStatus.valueOf(rs.getString("status")))
                .summary(rs.getString("summary"))
                .rootCause(rs.getString("root_cause"))
                .confidence(confidence)
                .aiModelUsed(rs.getString("ai_model_used"))
                .startedAt(toInstant(rs.getTimestamp("started_at")))
                .completedAt(toInstant(rs.getTimestamp("completed_at")))
                .createdAt(toInstant(rs.getTimestamp("created_at")))
                .updatedAt(toInstant(rs.getTimestamp("updated_at")))
                .build();
    };

    public Investigation save(Investigation inv) {
        jdbc.update("""
                INSERT INTO investigations (id, incident_id, status, summary, root_cause, confidence,
                    ai_model_used, started_at, completed_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                inv.getId(),
                inv.getIncidentId(),
                inv.getStatus().name(),
                inv.getSummary(),
                inv.getRootCause(),
                inv.getConfidence(),
                inv.getAiModelUsed(),
                toTimestamp(inv.getStartedAt()),
                toTimestamp(inv.getCompletedAt()),
                toTimestamp(inv.getCreatedAt()),
                toTimestamp(inv.getUpdatedAt()));
        return inv;
    }

    public Investigation update(Investigation inv) {
        jdbc.update("""
                UPDATE investigations SET status = ?, summary = ?, root_cause = ?, confidence = ?,
                    ai_model_used = ?, started_at = ?, completed_at = ?, updated_at = ?
                WHERE id = ?
                """,
                inv.getStatus().name(),
                inv.getSummary(),
                inv.getRootCause(),
                inv.getConfidence(),
                inv.getAiModelUsed(),
                toTimestamp(inv.getStartedAt()),
                toTimestamp(inv.getCompletedAt()),
                toTimestamp(inv.getUpdatedAt()),
                inv.getId());
        return inv;
    }

    public Optional<Investigation> findById(String id) {
        return jdbc.query("SELECT * FROM investigations WHERE id = ?", mapper, id).stream().findFirst();
    }

    public List<Investigation> findByIncidentId(String incidentId) {
        return jdbc.query("SELECT * FROM investigations WHERE incident_id = ? ORDER BY created_at DESC",
                mapper, incidentId);
    }

    private static Instant toInstant(Timestamp ts) {
        return ts == null ? null : ts.toInstant();
    }

    private static Timestamp toTimestamp(Instant instant) {
        return instant == null ? null : Timestamp.from(instant);
    }
}
