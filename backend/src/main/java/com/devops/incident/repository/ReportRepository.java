package com.devops.incident.repository;

import com.devops.incident.model.Report;
import com.devops.incident.model.enums.ReportFormat;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;

import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@Repository
public class ReportRepository {

    private final JdbcTemplate jdbc;

    public ReportRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    private final RowMapper<Report> mapper = (rs, rowNum) -> Report.builder()
            .id(rs.getString("id"))
            .incidentId(rs.getString("incident_id"))
            .title(rs.getString("title"))
            .content(rs.getString("content"))
            .format(ReportFormat.valueOf(rs.getString("format")))
            .metadata(rs.getString("metadata"))
            .generatedAt(toInstant(rs.getTimestamp("generated_at")))
            .createdAt(toInstant(rs.getTimestamp("created_at")))
            .build();

    public Report save(Report report) {
        jdbc.update("""
                INSERT INTO reports (id, incident_id, title, content, format, metadata, generated_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                report.getId(),
                report.getIncidentId(),
                report.getTitle(),
                report.getContent(),
                report.getFormat().name(),
                report.getMetadata(),
                toTimestamp(report.getGeneratedAt()),
                toTimestamp(report.getCreatedAt()));
        return report;
    }

    public Optional<Report> findById(String id) {
        return jdbc.query("SELECT * FROM reports WHERE id = ?", mapper, id).stream().findFirst();
    }

    public List<Report> findAll(String incidentId, int page, int size) {
        StringBuilder sql = new StringBuilder("SELECT * FROM reports WHERE 1=1");
        List<Object> params = new ArrayList<>();
        if (incidentId != null && !incidentId.isBlank()) {
            sql.append(" AND incident_id = ?");
            params.add(incidentId);
        }
        sql.append(" ORDER BY created_at DESC LIMIT ? OFFSET ?");
        params.add(size);
        params.add(page * size);
        return jdbc.query(sql.toString(), mapper, params.toArray());
    }

    public long count(String incidentId) {
        StringBuilder sql = new StringBuilder("SELECT COUNT(*) FROM reports WHERE 1=1");
        List<Object> params = new ArrayList<>();
        if (incidentId != null && !incidentId.isBlank()) {
            sql.append(" AND incident_id = ?");
            params.add(incidentId);
        }
        Long count = jdbc.queryForObject(sql.toString(), Long.class, params.toArray());
        return count == null ? 0 : count;
    }

    private static Instant toInstant(Timestamp ts) {
        return ts == null ? null : ts.toInstant();
    }

    private static Timestamp toTimestamp(Instant instant) {
        return instant == null ? null : Timestamp.from(instant);
    }
}
