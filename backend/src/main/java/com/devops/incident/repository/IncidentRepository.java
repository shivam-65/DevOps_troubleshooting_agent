package com.devops.incident.repository;

import com.devops.incident.model.Incident;
import com.devops.incident.model.enums.IncidentSeverity;
import com.devops.incident.model.enums.IncidentStatus;
import com.devops.incident.util.JsonUtil;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;

import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.Set;

@Repository
public class IncidentRepository {

    private static final Set<String> ALLOWED_SORT_FIELDS = Set.of("created_at", "updated_at", "severity");

    private final JdbcTemplate jdbc;

    public IncidentRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    private final RowMapper<Incident> mapper = (rs, rowNum) -> Incident.builder()
            .id(rs.getString("id"))
            .title(rs.getString("title"))
            .description(rs.getString("description"))
            .severity(IncidentSeverity.valueOf(rs.getString("severity")))
            .status(IncidentStatus.valueOf(rs.getString("status")))
            .affectedServices(JsonUtil.toStringList(rs.getString("affected_services")))
            .assignee(rs.getString("assignee"))
            .tags(JsonUtil.toStringList(rs.getString("tags")))
            .createdAt(toInstant(rs.getTimestamp("created_at")))
            .updatedAt(toInstant(rs.getTimestamp("updated_at")))
            .resolvedAt(toInstant(rs.getTimestamp("resolved_at")))
            .closedAt(toInstant(rs.getTimestamp("closed_at")))
            .build();

    public Incident save(Incident incident) {
        jdbc.update("""
                INSERT INTO incidents (id, title, description, severity, status, affected_services,
                    assignee, tags, created_at, updated_at, resolved_at, closed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                incident.getId(),
                incident.getTitle(),
                incident.getDescription(),
                incident.getSeverity().name(),
                incident.getStatus().name(),
                JsonUtil.toJson(incident.getAffectedServices()),
                incident.getAssignee(),
                JsonUtil.toJson(incident.getTags()),
                toTimestamp(incident.getCreatedAt()),
                toTimestamp(incident.getUpdatedAt()),
                toTimestamp(incident.getResolvedAt()),
                toTimestamp(incident.getClosedAt()));
        return incident;
    }

    public Incident update(Incident incident) {
        jdbc.update("""
                UPDATE incidents SET title = ?, description = ?, severity = ?, status = ?,
                    affected_services = ?, assignee = ?, tags = ?, updated_at = ?,
                    resolved_at = ?, closed_at = ?
                WHERE id = ?
                """,
                incident.getTitle(),
                incident.getDescription(),
                incident.getSeverity().name(),
                incident.getStatus().name(),
                JsonUtil.toJson(incident.getAffectedServices()),
                incident.getAssignee(),
                JsonUtil.toJson(incident.getTags()),
                toTimestamp(incident.getUpdatedAt()),
                toTimestamp(incident.getResolvedAt()),
                toTimestamp(incident.getClosedAt()),
                incident.getId());
        return incident;
    }

    public Optional<Incident> findById(String id) {
        List<Incident> results = jdbc.query("SELECT * FROM incidents WHERE id = ?", mapper, id);
        return results.stream().findFirst();
    }

    public boolean existsById(String id) {
        Integer count = jdbc.queryForObject("SELECT COUNT(*) FROM incidents WHERE id = ?", Integer.class, id);
        return count != null && count > 0;
    }

    public void deleteById(String id) {
        jdbc.update("DELETE FROM incidents WHERE id = ?", id);
    }

    public List<Incident> findAll(IncidentStatus status, IncidentSeverity severity, String search,
                                  String sortBy, String sortDir, int page, int size) {
        StringBuilder sql = new StringBuilder("SELECT * FROM incidents WHERE 1=1");
        List<Object> params = new ArrayList<>();
        if (status != null) {
            sql.append(" AND status = ?");
            params.add(status.name());
        }
        if (severity != null) {
            sql.append(" AND severity = ?");
            params.add(severity.name());
        }
        if (search != null && !search.isBlank()) {
            sql.append(" AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)");
            String like = "%" + search.toLowerCase() + "%";
            params.add(like);
            params.add(like);
        }
        sql.append(" ORDER BY ").append(resolveSortColumn(sortBy)).append(" ").append(resolveSortDir(sortDir));
        sql.append(" LIMIT ? OFFSET ?");
        params.add(size);
        params.add(page * size);
        return jdbc.query(sql.toString(), mapper, params.toArray());
    }

    public long count(IncidentStatus status, IncidentSeverity severity, String search) {
        StringBuilder sql = new StringBuilder("SELECT COUNT(*) FROM incidents WHERE 1=1");
        List<Object> params = new ArrayList<>();
        if (status != null) {
            sql.append(" AND status = ?");
            params.add(status.name());
        }
        if (severity != null) {
            sql.append(" AND severity = ?");
            params.add(severity.name());
        }
        if (search != null && !search.isBlank()) {
            sql.append(" AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)");
            String like = "%" + search.toLowerCase() + "%";
            params.add(like);
            params.add(like);
        }
        Long count = jdbc.queryForObject(sql.toString(), Long.class, params.toArray());
        return count == null ? 0 : count;
    }

    private String resolveSortColumn(String sortBy) {
        if (sortBy == null) {
            return "created_at";
        }
        String column = switch (sortBy) {
            case "createdAt" -> "created_at";
            case "updatedAt" -> "updated_at";
            case "severity" -> "severity";
            default -> sortBy;
        };
        return ALLOWED_SORT_FIELDS.contains(column) ? column : "created_at";
    }

    private String resolveSortDir(String sortDir) {
        return "asc".equalsIgnoreCase(sortDir) ? "ASC" : "DESC";
    }

    private static Instant toInstant(Timestamp ts) {
        return ts == null ? null : ts.toInstant();
    }

    private static Timestamp toTimestamp(Instant instant) {
        return instant == null ? null : Timestamp.from(instant);
    }
}
