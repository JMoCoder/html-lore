from dataclasses import replace

from ..schemas import ChecklistItem, ChecklistStatus, GenerationStage, PlanDraft, SectionPlan
from .base import GenerationAgent


class PlannerAgent(GenerationAgent):
    name = "Planner"
    stage = GenerationStage.PLANNING
    output_schema = PlanDraft

    def fake_payload(self, state):
        title = state.requirement_brief.user_goal if state.requirement_brief else "HTML note"
        sections = [
            {"id": "overview", "title": "Overview", "purpose": "Explain the core topic.", "expected_content": ["summary", "key points"]},
            {"id": "details", "title": "Details", "purpose": "Organize source material into readable sections.", "expected_content": ["structured content"]},
            {"id": "takeaways", "title": "Takeaways", "purpose": "Close with practical conclusions.", "expected_content": ["next steps"]},
        ]
        checklist = [
            {"id": "requirements", "title": "Requirements analyzed", "owner": "RequirementAnalyst", "status": "done"},
            {"id": "content", "title": "Content drafted", "owner": "ContentWriter", "status": "pending"},
            {"id": "style", "title": "Style brief prepared", "owner": "StyleDesigner", "status": "pending"},
            {"id": "html", "title": "HTML generated", "owner": "HTMLCoder", "status": "pending"},
            {"id": "verify", "title": "Output verified", "owner": "Verifier", "status": "pending"},
        ]
        return {
            "page_goal": title,
            "information_architecture": "Three-part note: overview, details, takeaways.",
            "section_plan": sections,
            "content_strategy": "Use uploaded material as source grounding and rewrite into concise explanatory prose.",
            "visual_strategy": "Create a clean readable HTML document with clear hierarchy.",
            "execution_checklist": checklist,
            "verification_targets": ["source coverage", "HTML validity", "static safety"],
        }

    def apply_output(self, state, output: PlanDraft):
        checklist = [ChecklistItem(**{**item.__dict__, "status": ChecklistStatus(item.status)}) if isinstance(item.status, str) else item for item in output.execution_checklist]
        return replace(state, plan_draft=output, execution_checklist=checklist)
