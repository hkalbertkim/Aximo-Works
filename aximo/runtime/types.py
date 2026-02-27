from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Protocol, Tuple


@dataclass
class ExecutionInput:
    deployment_id: str
    customer_id: str
    channel: str
    payload: Any
    received_at: datetime


@dataclass
class ExecutionContext:
    deployment_id: str
    customer_id: str
    config: Any
    knowledge: Any
    history: Any


@dataclass
class Action:
    action_type: str
    payload: Any


@dataclass
class ExecutionResult:
    ok: bool
    output: Any = None
    actions: List[Action] = field(default_factory=list)
    error: str | None = None


@dataclass
class Event:
    event_type: str
    timestamp: datetime
    customer_id: str
    deployment_id: str
    skill_id: str
    skill_version: str
    execution_id: str
    actor: str
    payload: Dict[str, Any] = field(default_factory=dict)


class EventSink(Protocol):
    def emit(self, event: Event) -> None:
        ...


class ActionDispatcher(Protocol):
    def dispatch(self, action: Action, ctx: ExecutionContext) -> None:
        ...


ConfigLoader = Callable[[str, str], Any]
KnowledgeLoader = Callable[[str, str], Any]
HistoryLoader = Callable[[str, str], Any]


class Skill(Protocol):
    def identify(self) -> Tuple[str, str]:
        ...

    def preprocess(self, input: ExecutionInput) -> Any:
        ...

    def build_context(
        self,
        input: ExecutionInput,
        config_loader: ConfigLoader,
        knowledge_loader: KnowledgeLoader,
        history_loader: HistoryLoader,
    ) -> ExecutionContext:
        ...

    def plan(self, context: ExecutionContext, normalized_input: Any) -> Dict[str, Any]:
        ...

    def run_llm(self, context: ExecutionContext, plan: Dict[str, Any]) -> Any:
        ...

    def postprocess(self, context: ExecutionContext, llm_output: Any) -> Tuple[Any, List[Action]]:
        ...
