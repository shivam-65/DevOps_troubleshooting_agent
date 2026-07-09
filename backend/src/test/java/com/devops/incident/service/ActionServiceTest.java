package com.devops.incident.service;

import com.devops.incident.adapter.ToolAdapterFactory;
import com.devops.incident.exception.InvalidStateTransitionException;
import com.devops.incident.model.Action;
import com.devops.incident.model.dto.request.ApproveActionRequest;
import com.devops.incident.model.dto.request.RejectActionRequest;
import com.devops.incident.model.dto.response.ActionResponse;
import com.devops.incident.model.enums.ActionStatus;
import com.devops.incident.model.enums.ActionType;
import com.devops.incident.repository.ActionRepository;
import com.devops.incident.repository.IncidentRepository;
import com.devops.incident.repository.InvestigationRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.Instant;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class ActionServiceTest {

    @Mock private ActionRepository actionRepository;
    @Mock private InvestigationRepository investigationRepository;
    @Mock private IncidentRepository incidentRepository;
    @Mock private ToolAdapterFactory adapterFactory;
    @Mock private EventPublisherService eventPublisher;

    @InjectMocks private ActionService actionService;

    private Action action(ActionStatus status) {
        Instant now = Instant.now();
        return Action.builder()
                .id("act-1")
                .investigationId("inv-1")
                .incidentId("inc-1")
                .type(ActionType.RESTART_SERVICE)
                .status(status)
                .title("Restart")
                .createdAt(now)
                .updatedAt(now)
                .build();
    }

    @Test
    void shouldApproveProposedAction() {
        when(actionRepository.findById("act-1")).thenReturn(Optional.of(action(ActionStatus.PROPOSED)));
        when(actionRepository.update(any())).thenAnswer(a -> a.getArgument(0));

        ApproveActionRequest req = new ApproveActionRequest();
        req.setApprovedBy("john.doe");

        ActionResponse response = actionService.approve("act-1", req);

        assertThat(response.getStatus()).isEqualTo(ActionStatus.APPROVED);
        assertThat(response.getApprovedBy()).isEqualTo("john.doe");
        assertThat(response.getApprovedAt()).isNotNull();
    }

    @Test
    void shouldRejectApproveWhenNotProposed() {
        when(actionRepository.findById("act-1")).thenReturn(Optional.of(action(ActionStatus.APPROVED)));

        ApproveActionRequest req = new ApproveActionRequest();
        req.setApprovedBy("john.doe");

        assertThatThrownBy(() -> actionService.approve("act-1", req))
                .isInstanceOf(InvalidStateTransitionException.class);
    }

    @Test
    void shouldRejectProposedAction() {
        when(actionRepository.findById("act-1")).thenReturn(Optional.of(action(ActionStatus.PROPOSED)));
        when(actionRepository.update(any())).thenAnswer(a -> a.getArgument(0));

        RejectActionRequest req = new RejectActionRequest();
        req.setReason("Too risky");

        ActionResponse response = actionService.reject("act-1", req);

        assertThat(response.getStatus()).isEqualTo(ActionStatus.REJECTED);
    }

    @Test
    void shouldNotExecuteUnlessApproved() {
        when(actionRepository.findById("act-1")).thenReturn(Optional.of(action(ActionStatus.PROPOSED)));

        assertThatThrownBy(() -> actionService.execute("act-1"))
                .isInstanceOf(InvalidStateTransitionException.class);
    }

    @Test
    void shouldTransitionToExecutingWhenApproved() {
        when(actionRepository.findById("act-1")).thenReturn(Optional.of(action(ActionStatus.APPROVED)));
        when(actionRepository.update(any())).thenAnswer(a -> a.getArgument(0));

        ActionResponse response = actionService.execute("act-1");

        assertThat(response.getStatus()).isEqualTo(ActionStatus.EXECUTING);
    }
}
