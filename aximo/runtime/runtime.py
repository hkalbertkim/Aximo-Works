from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from .types import (
    Action,
    ActionDispatcher,
    ConfigLoader,
    Event,
    EventSink,
    ExecutionInput,
    ExecutionResult,
    HistoryLoader,
    KnowledgeLoader,
    Skill,
)


def _emit_event(
    event_sink: EventSink,
    *,
    event_type: str,
    customer_id: str,
    deployment_id: str,
    skill_id: str,
    skill_version: str,
    execution_id: str,
    actor: str,
    payload: Dict[str, Any] | None = None,
) -> None:
    event_sink.emit(
        Event(
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            customer_id=customer_id,
            deployment_id=deployment_id,
            skill_id=skill_id,
            skill_version=skill_version,
            execution_id=execution_id,
            actor=actor,
            payload=payload or {},
        )
    )


def run_execution(
    skill: Skill,
    exec_input: ExecutionInput,
    config_loader: ConfigLoader,
    knowledge_loader: KnowledgeLoader,
    history_loader: HistoryLoader,
    action_dispatcher: ActionDispatcher,
    event_sink: EventSink,
    actor: str = "system",
) -> ExecutionResult:
    execution_id = str(uuid4())
    skill_id, skill_version = skill.identify()

    _emit_event(
        event_sink,
        event_type="execution_triggered",
        customer_id=exec_input.customer_id,
        deployment_id=exec_input.deployment_id,
        skill_id=skill_id,
        skill_version=skill_version,
        execution_id=execution_id,
        actor=actor,
        payload={"channel": exec_input.channel, "received_at": exec_input.received_at.isoformat()},
    )

    try:
        _emit_event(
            event_sink,
            event_type="execution_processing",
            customer_id=exec_input.customer_id,
            deployment_id=exec_input.deployment_id,
            skill_id=skill_id,
            skill_version=skill_version,
            execution_id=execution_id,
            actor=actor,
        )

        normalized_input = skill.preprocess(exec_input)
        context = skill.build_context(
            exec_input,
            config_loader=config_loader,
            knowledge_loader=knowledge_loader,
            history_loader=history_loader,
        )
        plan = skill.plan(context, normalized_input)
        llm_output = skill.run_llm(context, plan)
        output, actions = skill.postprocess(context, llm_output)

        for action in actions:
            _emit_event(
                event_sink,
                event_type="action_prepared",
                customer_id=exec_input.customer_id,
                deployment_id=exec_input.deployment_id,
                skill_id=skill_id,
                skill_version=skill_version,
                execution_id=execution_id,
                actor=actor,
                payload={"action_type": action.action_type},
            )
            try:
                action_dispatcher.dispatch(action, context)
            except Exception as dispatch_err:
                _emit_event(
                    event_sink,
                    event_type="action_failed",
                    customer_id=exec_input.customer_id,
                    deployment_id=exec_input.deployment_id,
                    skill_id=skill_id,
                    skill_version=skill_version,
                    execution_id=execution_id,
                    actor=actor,
                    payload={
                        "action_type": action.action_type,
                        "error": str(dispatch_err),
                    },
                )
                raise

            _emit_event(
                event_sink,
                event_type="action_dispatched",
                customer_id=exec_input.customer_id,
                deployment_id=exec_input.deployment_id,
                skill_id=skill_id,
                skill_version=skill_version,
                execution_id=execution_id,
                actor=actor,
                payload={"action_type": action.action_type},
            )

        _emit_event(
            event_sink,
            event_type="execution_completed",
            customer_id=exec_input.customer_id,
            deployment_id=exec_input.deployment_id,
            skill_id=skill_id,
            skill_version=skill_version,
            execution_id=execution_id,
            actor=actor,
            payload={"actions_count": len(actions)},
        )

        return ExecutionResult(ok=True, output=output, actions=actions)
    except Exception as err:
        _emit_event(
            event_sink,
            event_type="execution_failed",
            customer_id=exec_input.customer_id,
            deployment_id=exec_input.deployment_id,
            skill_id=skill_id,
            skill_version=skill_version,
            execution_id=execution_id,
            actor=actor,
            payload={"error": str(err)},
        )
        return ExecutionResult(ok=False, output=None, actions=[], error=str(err))
