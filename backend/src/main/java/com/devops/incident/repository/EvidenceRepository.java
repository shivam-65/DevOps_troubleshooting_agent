package com.devops.incident.repository;

import com.devops.incident.model.InvestigationEvidence;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;

import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;

@Repository
public class EvidenceRepository {

    private final JdbcTemplate jdbc;

    public EvidenceRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    private final RowMapper<InvestigationEvidence> mapper = (rs, rowNum) -> InvestigationEvidence.builder()
            .id(rs.getString("id"))
            .investigationId(rs.getString("investigation_id"))
            .source(rs.getString("source"))
            .type(rs.getString("type"))
            .data(rs.getString("data"))
            .collectedAt(toInstant(rs.getTimestamp("collected_at")))
            .build();

    public InvestigationEvidence save(InvestigationEvidence evidence) {
        jdbc.update("""
                INSERT INTO investigation_evidence (id, investigation_id, source, type, data, collected_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                evidence.getId(),
                evidence.getInvestigationId(),
                evidence.getSource(),
                evidence.getType(),
                evidence.getData(),
                toTimestamp(evidence.getCollectedAt()));
        return evidence;
    }

    public List<InvestigationEvidence> findByInvestigationId(String investigationId) {
        return jdbc.query("SELECT * FROM investigation_evidence WHERE investigation_id = ? ORDER BY collected_at ASC",
                mapper, investigationId);
    }

    private static Instant toInstant(Timestamp ts) {
        return ts == null ? null : ts.toInstant();
    }

    private static Timestamp toTimestamp(Instant instant) {
        return instant == null ? null : Timestamp.from(instant);
    }
}
