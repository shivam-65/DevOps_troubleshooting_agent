package com.devops.incident.service;

import com.devops.incident.exception.InvalidStateTransitionException;
import com.devops.incident.exception.ResourceNotFoundException;
import com.devops.incident.model.Incident;
import com.devops.incident.model.dto.request.CreateIncidentRequest;
import com.devops.incident.model.dto.request.UpdateIncidentRequest;
import com.devops.incident.model.dto.response.IncidentResponse;
import com.devops.incident.model.enums.IncidentSeverity;
import com.devops.incident.model.enums.IncidentStatus;
import com.devops.incident.repository.IncidentRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.Instant;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class IncidentServiceTest {

    @Mock
    private IncidentRepository incidentRepository;

    @Mock
    private EventPublisherService eventPublisher;

    @InjectMocks
    private IncidentService incidentService;

    private Incident incident(IncidentStatus status) {
        Instant now = Instant.now();
        return Incident.builder()
                .id("inc-1")
                .title("Test")
                .description("Desc")
                .severity(IncidentSeverity.HIGH)
                .status(status)
                .createdAt(now)
                .updatedAt(now)
                .build();
    }

    @Test
    void shouldCreateIncidentWithOpenStatus() {
        CreateIncidentRequest req = new CreateIncidentRequest();
        req.setTitle("Payment latency");
        req.setDescription("5x latency");
        req.setSeverity(IncidentSeverity.HIGH);
        req.setAffectedServices(List.of("payment-api"));

        when(incidentRepository.save(any())).thenAnswer(a -> a.getArgument(0));

        IncidentResponse response = incidentService.create(req);

        assertThat(response.getStatus()).isEqualTo(IncidentStatus.OPEN);
        assertThat(response.getId()).isNotBlank();
        verify(eventPublisher).publishIncidentEvent(org.mockito.ArgumentMatchers.eq("INCIDENT_CREATED"), anyString(), any());
    }

    @Test
    void shouldRejectInvalidStatusTransition() {
        when(incidentRepository.findById("inc-1")).thenReturn(Optional.of(incident(IncidentStatus.CLOSED)));

        assertThatThrownBy(() -> incidentService.updateStatus("inc-1", IncidentStatus.INVESTIGATING))
                .isInstanceOf(InvalidStateTransitionException.class);

        verify(incidentRepository, never()).update(any());
    }

    @Test
    void shouldSetResolvedAtWhenTransitioningToResolved() {
        when(incidentRepository.findById("inc-1")).thenReturn(Optional.of(incident(IncidentStatus.INVESTIGATING)));
        when(incidentRepository.update(any())).thenAnswer(a -> a.getArgument(0));

        IncidentResponse response = incidentService.updateStatus("inc-1", IncidentStatus.RESOLVED);

        assertThat(response.getStatus()).isEqualTo(IncidentStatus.RESOLVED);
        assertThat(response.getResolvedAt()).isNotNull();
    }

    @Test
    void shouldThrowWhenIncidentNotFound() {
        when(incidentRepository.findById("missing")).thenReturn(Optional.empty());

        assertThatThrownBy(() -> incidentService.getById("missing"))
                .isInstanceOf(ResourceNotFoundException.class);
    }

    @Test
    void shouldAllowOpenToInvestigatingTransitionViaUpdate() {
        when(incidentRepository.findById("inc-1")).thenReturn(Optional.of(incident(IncidentStatus.OPEN)));
        when(incidentRepository.update(any())).thenAnswer(a -> a.getArgument(0));

        UpdateIncidentRequest req = new UpdateIncidentRequest();
        req.setStatus(IncidentStatus.INVESTIGATING);

        IncidentResponse response = incidentService.update("inc-1", req);

        assertThat(response.getStatus()).isEqualTo(IncidentStatus.INVESTIGATING);
    }
}
