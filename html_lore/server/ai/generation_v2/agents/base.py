from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from ..fake_model import FakeGenerationModelClient
from ..model_client import GenerationJsonModelClient, agent_payload
from ..schema_loader import AgentOutputSchemaError, parse_dataclass_json
from ..schemas import ChecklistStatus, GenerationStage, GenerationState, SkillTraceEntry, normalize_for_json
from ..skills.loader import LoadedSkill, load_default_skills_for_agent
from ..state import complete_stage, fail_stage, start_stage


MAX_SCHEMA_RETRIES = 2


@dataclass(frozen=True)
class GenerationAgentResult:
    state: GenerationState
    message: str = ""


class GenerationAgent:
    name = "GenerationAgent"
    stage = GenerationStage.QUEUED
    output_schema: type[Any] | None = None

    def __init__(self, model_client: GenerationJsonModelClient | None = None) -> None:
        self.model_client = model_client or FakeGenerationModelClient()
        self.skills = load_default_skills_for_agent(self.name)

    def run(self, state: GenerationState) -> GenerationAgentResult:
        next_state = start_stage(state, self.stage, agent=self.name, message=f"{self.name} started.")
        try:
            output = self.invoke_structured(next_state)
            next_state = self.apply_output(next_state, output)
            next_state = self.record_skill_trace(next_state)
            next_state = self.update_execution_checklist(next_state, ChecklistStatus.COMPLETED)
            next_state = complete_stage(next_state, self.stage, message=f"{self.name} completed.")
            return GenerationAgentResult(state=next_state, message=f"{self.name} completed.")
        except AgentOutputSchemaError as exc:
            next_state = self.record_schema_failure(next_state)
            retries = next_state.same_node_retries.get(self.name, 0)
            if retries <= MAX_SCHEMA_RETRIES:
                return self.run(next_state)
            next_state = self.update_execution_checklist(next_state, ChecklistStatus.FAILED, notes=str(exc))
            next_state = fail_stage(next_state, self.stage, message=str(exc), retryable=True)
            return GenerationAgentResult(state=next_state, message=str(exc))

    def invoke_structured(self, state: GenerationState) -> Any:
        if self.output_schema is None:
            raise AgentOutputSchemaError(f"{self.name} has no output schema.")
        raw = self.model_client.complete_json(
            node=self.name,
            schema_name=self.output_schema.__name__,
            payload=agent_payload(node=self.name, schema=self.output_schema, state=state, fallback=self.fake_payload(state), skills=self.skills),
            attempt=state.same_node_retries.get(self.name, 0),
        )
        return parse_dataclass_json(raw, self.output_schema)

    def fake_payload(self, state: GenerationState) -> dict[str, Any]:
        return {}

    def apply_output(self, state: GenerationState, output: Any) -> GenerationState:
        raise NotImplementedError

    def record_schema_failure(self, state: GenerationState) -> GenerationState:
        retries = dict(state.same_node_retries)
        retries[self.name] = retries.get(self.name, 0) + 1
        return replace(state, same_node_retries=retries)

    def record_skill_trace(self, state: GenerationState) -> GenerationState:
        if not self.skills:
            return state
        seen = {(entry.agent, entry.id) for entry in state.skill_trace}
        trace = list(state.skill_trace)
        for skill in self.skills:
            if (self.name, skill.id) in seen:
                continue
            trace.append(skill_trace_entry(self.name, skill))
        return replace(state, skill_trace=trace)

    def update_execution_checklist(self, state: GenerationState, status: ChecklistStatus, *, notes: str = "") -> GenerationState:
        if not state.execution_checklist:
            return state
        checklist = []
        changed = False
        for item in state.execution_checklist:
            if checklist_item_owner_matches_agent(item.owner, self.name):
                checklist.append(replace(item, status=status, notes=notes or item.notes))
                changed = True
            else:
                checklist.append(item)
        return replace(state, execution_checklist=checklist) if changed else state


def checklist_item_owner_matches_agent(owner: str, agent_name: str) -> bool:
    normalized_owner = "".join(str(owner or "").lower().split())
    normalized_agent = "".join(str(agent_name or "").lower().split())
    aliases = {
        "writer": "contentwriter",
        "contentwriter": "contentwriter",
        "contentwriteragent": "contentwriter",
        "designer": "styledesigner",
        "styledesigner": "styledesigner",
        "styledesigneragent": "styledesigner",
        "coder": "htmlcoder",
        "htmlcoder": "htmlcoder",
        "htmlcoderagent": "htmlcoder",
        "verifier": "verifier",
        "verifieragent": "verifier",
        "safety": "safetyreviewer",
        "safetyreviewer": "safetyreviewer",
        "safetyrevieweragent": "safetyreviewer",
        "planner": "planner",
        "planneragent": "planner",
        "requirementanalyst": "requirementanalyst",
        "requirementanalystagent": "requirementanalyst",
        "finalizer": "finalizer",
        "finalizeragent": "finalizer",
    }
    return aliases.get(normalized_owner, normalized_owner) == aliases.get(normalized_agent, normalized_agent)


def skill_trace_entry(agent_name: str, skill: LoadedSkill) -> SkillTraceEntry:
    return SkillTraceEntry(id=skill.id, title=skill.title, agent=agent_name, version=skill.version, source=skill.source)


def first_non_empty(*values: str) -> str:
    for value in values:
        if str(value or "").strip():
            return str(value).strip()
    return ""


def short_text(value: str, limit: int = 280) -> str:
    cleaned = " ".join(str(value or "").split())
    return cleaned[:limit]


def public_dict(value: Any) -> dict[str, Any]:
    return normalize_for_json(asdict(value))
