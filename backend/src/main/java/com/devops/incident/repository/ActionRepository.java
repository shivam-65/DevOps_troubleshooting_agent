package com.devops.incident.repository;

import com.devops.incident.model.Action;
import com.devops.incident.model.enums.ActionStatus;
import com.devops.incident.model.enums.ActionType;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;

import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Repository
public class ActionRepository {

    private final JdbcTemplate jdbc;

    public ActionRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    private final RowMapper<Action> mapper = (rs, rowNum) -> Action.builder()
            .id(rs.getString("id"))
            .investigationId(rs.getString("investigation_id"))
            .incidentId(rs.getString("incident_id"))
            .type(ActionType.valueOf(rs.getString("type")))
            .status(ActionStatus.valueOf(rs.getString("status")))
            .title(rs.getString("title"))
            .description(rs.getString("description"))
            .command(rs.getString("command"))
            .targetService(rs.getString("target_service"))
            .parameters(rs.getString("parameters"))
            .risk(rs.getString("risk"))
            .estimatedImpact(rs.getString("estimated_impact"))
            .executionResult(rs.getString("execution_result"))
            .approvedBy(rs.getString("approved_by"))
            .approvedAt(toInstant(rs.getTimestamp("approved_at")))
            .executedAt(toInstant(rs.getTimestamp("executed_at")))
            .completedAt(toInstant(rs.getTimestamp("completed_at")))
            .createdAt(toInstant(rs.getTimestamp("created_at")))
            .updatedAt(toInstant(rs.getTimestamp("updated_at")))
            .build();

    public Action save(Action action) {
        jdbc.update("""
                INSERT INTO actions (id, investigation_id, incident_id, type, status, title, description,
                    command, target_service, parameters, risk, estimated_impact, execution_result,
                    approved_by, approved_at, executed_at, completed_at, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                action.getId(),
                action.getInvestigationId(),
                action.getIncidentId(),
                action.getType().name(),
                action.getStatus().name(),
                action.getTitle(),
                action.getDescription(),
                action.getCommand(),
                action.getTargetService(),
                action.getParameters(),
                action.getRisk(),
                action.getEstimatedImpact(),
                action.getExecutionResult(),
                action.getApprovedBy(),
                toTimestamp(action.getApprovedAt()),
                toTimestamp(action.getExecutedAt()),
                toTimestamp(action.getCompletedAt()),
                toTimestamp(action.getCreatedAt()),
                toTimestamp(action.getUpdatedAt()));
        return action;
    }

    public Action update(Action action) {
        jdbc.update("""
                UPDATE actions SET status = ?, title = ?, description = ?, command = ?, target_service = ?,
                    parameters = ?, risk = ?, estimated_impact = ?, execution_result = ?, approved_by = ?,
                    approved_at = ?, executed_at = ?, completed_at = ?, updated_at = ?
                WHERE id = ?
                """,
                action.getStatus().name(),
                action.getTitle(),
                action.getDescription(),
                action.getCommand(),
                action.getTargetService(),
                action.getParameters(),
                action.getRisk(),
                action.getEstimatedImpact(),
                action.getExecutionResult(),
                action.getApprovedBy(),
                toTimestamp(action.getApprovedAt()),
                toTimestamp(action.getExecutedAt()),
                toTimestamp(action.getCompletedAt()),
                toTimestamp(action.getUpdatedAt()),
                action.getId());
        return action;
    }

    public Optional<Action> findById(String id) {
        return jdbc.query("SELECT * FROM actions WHERE id = ?", mapper, id).stream().findFirst();
    }

    public List<Action> findByInvestigationId(String investigationId) {
        return jdbc.query("SELECT * FROM actions WHERE investigation_id = ? ORDER BY created_at ASC",
                mapper, investigationId);
    }

    public List<Action> findAll(String incidentId, String investigationId, ActionStatus status,
                                int page, int size) {
        StringBuilder sql = new StringBuilder("SELECT * FROM actions WHERE 1=1");
        List<Object> params = filterParams(sql, incidentId, investigationId, status);
        sql.append(" ORDER BY created_at DESC LIMIT ? OFFSET ?");
        params.add(size);
        params.add(page * size);
        return jdbc.query(sql.toString(), mapper, params.toArray());
    }

    public long count(String incidentId, String investigationId, ActionStatus status) {
        StringBuilder sql = new StringBuilder("SELECT COUNT(*) FROM actions WHERE 1=1");
        List<Object> params = filterParams(sql, incidentId, investigationId, status);
        Long count = jdbc.queryForObject(sql.toString(), Long.class, params.toArray());
        return count == null ? 0 : count;
    }

    private List<Object> filterParams(StringBuilder sql, String incidentId, String investigationId, ActionStatus status) {
        List<Object> params = new ArrayList<>();
        if (incidentId != null && !incidentId.isBlank()) {
            sql.append(" AND incident_id = ?");
            params.add(incidentId);
        }
        if (investigationId != null && !investigationId.isBlank()) {
            sql.append(" AND investigation_id = ?");
            params.add(investigationId);
        }
        if (status != null) {
            sql.append(" AND status = ?");
            params.add(status.name());
        }
        return params;
    }

    private static Instant toInstant(Timestamp ts) {
        return ts == null ? null : ts.toInstant();
    }

    private static Timestamp toTimestamp(Instant instant) {
        return instant == null ? null : Timestamp.from(instant);
    }
}
