package com.devops.incident.service;

import com.devops.incident.integration.AIServiceClient;
import com.devops.incident.integration.dto.AIAnalysisResult;
import com.devops.incident.integration.dto.AIRecommendedAction;
import com.devops.incident.model.Investigation;
import com.devops.incident.model.dto.response.InvestigationResponse;
import com.devops.incident.model.enums.InvestigationStatus;
import com.devops.incident.repository.ActionRepository;
import com.devops.incident.repository.EvidenceRepository;
import com.devops.incident.repository.IncidentRepository;
import com.devops.incident.repository.InvestigationRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.Instant;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class InvestigationServiceTest {

    @Mock private InvestigationRepository investigationRepository;
    @Mock private EvidenceRepository evidenceRepository;
    @Mock private ActionRepository actionRepository;
    @Mock private IncidentRepository incidentRepository;
    @Mock private AIServiceClient aiServiceClient;
    @Mock private EventPublisherService eventPublisher;

    private InvestigationService service;

    @BeforeEach
    void setUp() {
        service = new InvestigationService(investigationRepository, evidenceRepository, actionRepository,
                incidentRepository, aiServiceClient, eventPublisher, "http://localhost:8080", null);
    }

    private Investigation investigation() {
        Instant now = Instant.now();
        return Investigation.builder()
                .id("inv-1")
                .incidentId("inc-1")
                .status(InvestigationStatus.IN_PROGRESS)
                .createdAt(now)
                .updatedAt(now)
                .build();
    }

    @Test
    void shouldProcessCompletedCallbackAndCreateActions() {
        when(investigationRepository.findById("inv-1")).thenReturn(Optional.of(investigation()));
        when(investigationRepository.update(any())).thenAnswer(a -> a.getArgument(0));
        when(evidenceRepository.findByInvestigationId("inv-1")).thenReturn(List.of());
        when(actionRepository.findByInvestigationId("inv-1")).thenReturn(List.of());

        AIRecommendedAction ra = AIRecommendedAction.builder()
                .type("RESTART_SERVICE")
                .title("Restart payment-api")
                .targetService("payment-api")
                .risk("MEDIUM")
                .build();
        AIAnalysisResult result = AIAnalysisResult.builder()
                .investigationId("inv-1")
                .status("COMPLETED")
                .summary("Memory leak found")
                .rootCause("Unclosed connections")
                .confidence(0.87)
                .aiModelUsed("gemini")
                .recommendedActions(List.of(ra))
                .build();

        InvestigationResponse response = service.processCallback("inv-1", result);

        assertThat(response.getStatus()).isEqualTo(InvestigationStatus.COMPLETED);
        verify(actionRepository).save(any());
        verify(eventPublisher).publishInvestigationEvent(
                org.mockito.ArgumentMatchers.eq("INVESTIGATION_COMPLETED"),
                org.mockito.ArgumentMatchers.eq("inc-1"),
                org.mockito.ArgumentMatchers.eq("inv-1"), any());
    }

    @Test
    void shouldMarkFailedOnFailedCallback() {
        when(investigationRepository.findById("inv-1")).thenReturn(Optional.of(investigation()));
        when(investigationRepository.update(any())).thenAnswer(a -> a.getArgument(0));
        when(evidenceRepository.findByInvestigationId("inv-1")).thenReturn(List.of());
        when(actionRepository.findByInvestigationId("inv-1")).thenReturn(List.of());

        AIAnalysisResult result = AIAnalysisResult.builder()
                .investigationId("inv-1")
                .status("FAILED")
                .summary("AI timeout")
                .build();

        InvestigationResponse response = service.processCallback("inv-1", result);

        assertThat(response.getStatus()).isEqualTo(InvestigationStatus.FAILED);
    }
}
