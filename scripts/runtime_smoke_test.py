from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from aximo.runtime.runtime import run_execution
from aximo.runtime.types import Action, Event, ExecutionContext, ExecutionInput


class DummyEventSink:
    def __init__(self) -> None:
        self.events: list[Event] = []

    def emit(self, event: Event) -> None:
        self.events.append(event)


class DummyActionDispatcher:
    def __init__(self, fail_on_type: str | None = None) -> None:
        self.fail_on_type = fail_on_type
        self.dispatched: list[Action] = []

    def dispatch(self, action: Action, ctx: ExecutionContext) -> None:
        if self.fail_on_type and action.action_type == self.fail_on_type:
            raise RuntimeError(f"forced dispatch failure for {action.action_type}")
        self.dispatched.append(action)


class DummySkill:
    def identify(self) -> tuple[str, str]:
        return "dummy-skill", "1.0.0"

    def preprocess(self, input: ExecutionInput) -> dict[str, Any]:
        return {"normalized_payload": input.payload}

    def build_context(
        self,
        input: ExecutionInput,
        config_loader,
        knowledge_loader,
        history_loader,
    ) -> ExecutionContext:
        return ExecutionContext(
            deployment_id=input.deployment_id,
            customer_id=input.customer_id,
            config=config_loader(input.deployment_id, input.customer_id),
            knowledge=knowledge_loader(input.deployment_id, input.customer_id),
            history=history_loader(input.deployment_id, input.customer_id),
        )

    def plan(self, context: ExecutionContext, normalized_input: Any) -> dict[str, Any]:
        return {"intent": "test-plan", "normalized_input": normalized_input}

    def run_llm(self, context: ExecutionContext, plan: dict[str, Any]) -> dict[str, Any]:
        return {"text": "ok", "plan": plan}

    def postprocess(self, context: ExecutionContext, llm_output: Any) -> tuple[Any, list[Action]]:
        output = {"message": "smoke test success", "llm": llm_output}
        actions = [Action(action_type="notify", payload={"target": "console"})]
        return output, actions


def config_loader(deployment_id: str, customer_id: str) -> dict[str, Any]:
    return {"deployment_id": deployment_id, "customer_id": customer_id, "feature": "smoke"}


def knowledge_loader(deployment_id: str, customer_id: str) -> dict[str, Any]:
    return {"kb": f"knowledge-for-{deployment_id}-{customer_id}"}


def history_loader(deployment_id: str, customer_id: str) -> list[dict[str, str]]:
    return [{"role": "user", "content": "previous interaction"}]


def print_event_types(label: str, sink: DummyEventSink) -> None:
    print(label)
    for event in sink.events:
        print(event.event_type)


def main() -> None:
    skill = DummySkill()
    exec_input = ExecutionInput(
        deployment_id="dep-123",
        customer_id="cust-456",
        channel="test-channel",
        payload={"text": "hello"},
        received_at=datetime.now(timezone.utc),
    )

    sink_ok = DummyEventSink()
    dispatcher_ok = DummyActionDispatcher()

    result_ok = run_execution(
        skill=skill,
        exec_input=exec_input,
        config_loader=config_loader,
        knowledge_loader=knowledge_loader,
        history_loader=history_loader,
        action_dispatcher=dispatcher_ok,
        event_sink=sink_ok,
        actor="system",
    )

    print("=== FIRST RUN (SUCCESS) ===")
    print(f"ok={result_ok.ok}")
    print(f"dispatched_actions={len(dispatcher_ok.dispatched)}")
    print_event_types("event_types:", sink_ok)

    sink_fail = DummyEventSink()
    dispatcher_fail = DummyActionDispatcher(fail_on_type="notify")

    result_fail = run_execution(
        skill=skill,
        exec_input=exec_input,
        config_loader=config_loader,
        knowledge_loader=knowledge_loader,
        history_loader=history_loader,
        action_dispatcher=dispatcher_fail,
        event_sink=sink_fail,
        actor="system",
    )

    print("=== SECOND RUN (FORCED DISPATCH FAILURE) ===")
    print(f"ok={result_fail.ok}")
    print(f"error={result_fail.error}")
    print(f"dispatched_actions={len(dispatcher_fail.dispatched)}")
    print_event_types("event_types:", sink_fail)


if __name__ == "__main__":
    main()
