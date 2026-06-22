from __future__ import annotations

from dataclasses import replace
from typing import Callable
from uuid import uuid4

from .agents.content_writer import ContentWriterAgent
from .agents.finalizer import FinalizerAgent
from .agents.html_coder import HTMLCoderAgent
from .agents.planner import PlannerAgent
from .agents.requirement_analyst import RequirementAnalystAgent
from .agents.safety_reviewer import SafetyReviewerAgent
from .agents.style_designer import StyleDesignerAgent
from .agents.verifier import VerifierAgent
from .fake_model import FakeGenerationModelClient
from .model_client import GenerationJsonModelClient
from .orchestrator import GenerationOrchestrator
from .schemas import GenerationInput, GenerationStage, GenerationState
from .state import complete_stage, start_stage
from .tools.document_parser import parse_document
from .tools.style_hint_extractor import extract_style_hints


StateCallback = Callable[[GenerationState], None]


class HtmlGenerationV2Graph:
    name = "HtmlGenerationV2.alpha"

    def __init__(self, *, model_client: GenerationJsonModelClient | None = None, parser_mode: str = "markitdown", on_state: StateCallback | None = None) -> None:
        self.model_client = model_client or FakeGenerationModelClient()
        self.parser_mode = parser_mode
        self.on_state = on_state
        self.orchestrator = GenerationOrchestrator()
        self.agents = {
            "requirement_analyst": RequirementAnalystAgent(self.model_client),
            "planner": PlannerAgent(self.model_client),
            "content_writer": ContentWriterAgent(self.model_client),
            "style_designer": StyleDesignerAgent(self.model_client),
            "html_coder": HTMLCoderAgent(self.model_client),
            "verifier": VerifierAgent(self.model_client),
            "safety_reviewer": SafetyReviewerAgent(self.model_client),
            "finalizer": FinalizerAgent(self.model_client),
        }

    def initial_state(self, generation_input: GenerationInput, *, job_id: str = "", run_id: str = "") -> GenerationState:
        return GenerationState(job_id=job_id, run_id=run_id or uuid4().hex, input=generation_input)

    def run(self, state: GenerationState) -> GenerationState:
        next_state = state
        for _ in range(32):
            decision = self.orchestrator.decide_next(next_state)
            if decision.next_node == "write_gateway":
                return replace(next_state, current_step=GenerationStage.COMPLETED.value)
            if decision.next_node == "max_revision_rounds":
                return replace(next_state, failed_steps=[*next_state.failed_steps, decision.next_node])
            if decision.next_node == "ingest":
                next_state = self.run_ingest(next_state)
                self.emit_state(next_state)
                continue
            agent = self.agents.get(decision.next_node)
            if agent is None:
                return replace(next_state, failed_steps=[*next_state.failed_steps, decision.next_node])
            result = agent.run(next_state)
            next_state = result.state
            self.emit_state(next_state)
            if next_state.failed_steps:
                return next_state
        return replace(next_state, failed_steps=[*next_state.failed_steps, "max_graph_steps"])

    def emit_state(self, state: GenerationState) -> None:
        if self.on_state is None:
            return
        self.on_state(state)

    def run_ingest(self, state: GenerationState) -> GenerationState:
        next_state = start_stage(state, GenerationStage.PARSING, agent="Ingest", message="Parsing uploaded material.")
        parsed = parse_document(
            filename=state.input.filename or "source.txt",
            content=state.input.content,
            content_type=state.input.content_type,
            parser_mode=self.parser_mode,
        )
        parsed = replace(parsed, style_hints=extract_style_hints(parsed, role="material"))
        parsed_style_reference = None
        if state.input.reference_style == "file" and state.input.reference_file_name and state.input.reference_content:
            parsed_style_reference = parse_document(
                filename=state.input.reference_file_name,
                content=state.input.reference_content,
                content_type=state.input.reference_file_type,
                reference_role="style_reference",
                parser_mode=self.parser_mode,
            )
            parsed_style_reference = replace(parsed_style_reference, style_hints=extract_style_hints(parsed_style_reference, role="style_reference"))
        next_state = replace(next_state, parsed_document=parsed, parsed_style_reference=parsed_style_reference)
        return complete_stage(next_state, GenerationStage.PARSING, message="Uploaded material parsed.")
