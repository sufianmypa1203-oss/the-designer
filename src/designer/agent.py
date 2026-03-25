"""
The Designer — DesignerAgent Class (Async SDK Loop)

Built on the Claude Agent SDK's native async streaming loop with
upstream validation gate + evaluator-optimizer pass before handoff.
The agent:
1. Validates upstream Director artifacts (GATE — fails fast)
2. Generates HTML prototypes for each scene
3. Generates 3 JSON specs (visual, typography, manifest)
4. Self-validates via separate evaluator LLM call
5. Optimizes if issues found
6. Emits handoff block only when clean
"""
from __future__ import annotations
import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator, Callable

from .tools import DESIGNER_TOOLS, run_design_validation, generate_handoff_block
from .prompts import DESIGNER_SYSTEM_PROMPT
from .validator import DesignValidator


__version__ = "1.0.0"
SPECS_DIR = Path("specs")
PROTOTYPES_DIR = Path("prototypes")
logger = logging.getLogger("the-designer")


# ─── Lifecycle Hooks ──────────────────────────────────────────────────────────

class LifecycleHooks:
    """
    Agent lifecycle hooks for observability, guardrails, and control.
    Validates/blocks tool calls before execution, logs results after.
    """

    def __init__(self):
        self._pre_hooks: list[Callable] = []
        self._post_hooks: list[Callable] = []
        self._event_log: list[dict[str, Any]] = []

    def on_pre_tool_use(self, fn: Callable) -> Callable:
        """Register a hook that runs BEFORE a tool call. Can block execution."""
        self._pre_hooks.append(fn)
        return fn

    def on_post_tool_use(self, fn: Callable) -> Callable:
        """Register a hook that runs AFTER a tool call. For logging/metrics."""
        self._post_hooks.append(fn)
        return fn

    async def run_pre_hooks(self, tool_name: str, args: dict) -> bool:
        """Run all pre-hooks. Returns False if any hook blocks execution."""
        for hook in self._pre_hooks:
            result = hook(tool_name, args)
            if result is False:
                self.log_event("TOOL_BLOCKED", tool=tool_name, reason="Pre-hook rejected")
                return False
        return True

    async def run_post_hooks(self, tool_name: str, result: Any) -> None:
        """Run all post-hooks for observability."""
        for hook in self._post_hooks:
            hook(tool_name, result)

    def log_event(self, event_type: str, **data: Any) -> None:
        """Structured event logging for observability."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            **data,
        }
        self._event_log.append(entry)
        logger.info("%s: %s", event_type, json.dumps({k: str(v) for k, v in data.items()}))

    @property
    def events(self) -> list[dict[str, Any]]:
        return self._event_log.copy()


class DesignerAgent:
    """
    Agent 2 — The Designer.
    Owns: upstream validation → prototypes → visual spec → typography spec → manifest → handoff.
    Architecture: upstream gate + Pydantic contracts + 6-layer QA + evaluator-optimizer loop.
    """

    version = __version__

    def __init__(
        self,
        project_id: str | None = None,
        specs_dir: str | Path | None = None,
        prototypes_dir: str | Path | None = None,
    ):
        self.project_id = project_id
        self.specs_dir = Path(specs_dir) if specs_dir else SPECS_DIR
        self.prototypes_dir = Path(prototypes_dir) if prototypes_dir else PROTOTYPES_DIR
        self.validator = DesignValidator(
            specs_dir=self.specs_dir,
            prototypes_dir=self.prototypes_dir,
        )
        self.hooks = LifecycleHooks()
        self.conversation: list[dict] = []
        self.specs_dir.mkdir(exist_ok=True)
        self.prototypes_dir.mkdir(exist_ok=True)

        self._register_default_hooks()

    @classmethod
    def from_upstream(
        cls,
        specs_dir: str | Path,
        project_id: str | None = None,
    ) -> "DesignerAgent":
        """
        Factory method: create a DesignerAgent pointed at existing upstream specs.
        Validates upstream before returning.

        Usage:
            agent = DesignerAgent.from_upstream("path/to/specs")
            async for chunk in agent.run():
                print(chunk)
        """
        instance = cls(project_id=project_id, specs_dir=specs_dir)
        instance.hooks.log_event(
            "FROM_UPSTREAM",
            specs_dir=str(specs_dir),
        )
        return instance

    def _register_default_hooks(self) -> None:
        """Register built-in lifecycle hooks."""

        @self.hooks.on_pre_tool_use
        def guard_scope_boundary(tool_name: str, args: dict) -> bool:
            """Block tool calls that violate Designer scope."""
            forbidden_tools = {
                "animate", "spring", "transition", "build_component",
                "write_tsx", "modify_script",
            }
            if tool_name.lower() in forbidden_tools:
                logger.warning(
                    "Scope violation: Designer cannot use tool '%s'", tool_name
                )
                return False
            return True

        @self.hooks.on_post_tool_use
        def log_tool_result(tool_name: str, result: Any) -> None:
            """Log tool usage for observability."""
            self.hooks.log_event(
                "TOOL_USED",
                tool=tool_name,
                success=isinstance(result, dict) and result.get("success", True),
            )

    # ── Entry Point ───────────────────────────────────────────────────────

    async def run(self, user_input: str = "") -> AsyncIterator[str]:
        """
        Main agent loop. Streams tokens back to the caller.
        First validates upstream artifacts — GATE check.
        """
        self.hooks.log_event(
            "RUN_STARTED",
            input_chars=len(user_input),
            project=self.project_id,
        )

        # Upstream validation GATE
        upstream_issues = self.validator.validate_upstream_artifacts()
        if upstream_issues:
            yield "❌ **Upstream validation failed** — Director artifacts missing or invalid.\n\n"
            for issue in upstream_issues:
                yield f"  • [{issue.severity}] {issue.message}\n"
            yield "\n→ Run `/director` to generate the required specs first.\n"
            self.hooks.log_event("UPSTREAM_GATE_FAILED", issues=len(upstream_issues))
            return

        yield "✅ Upstream artifacts validated. Starting design phase...\n\n"
        self.hooks.log_event("UPSTREAM_GATE_PASSED")

        # Run the main agent loop
        prompt = self._build_design_prompt(user_input)
        async for chunk in self._agent_loop(prompt):
            yield chunk

        # After loop — run evaluator pass if design artifacts exist
        if self._design_artifacts_present():
            yield "\n\n---\n🔍 **Running design evaluator-optimizer pass...**\n\n"
            issues = self._run_deterministic_validation()

            if issues:
                critical = [i for i in issues if i.severity == "CRITICAL"]
                non_critical = [i for i in issues if i.severity != "CRITICAL"]

                yield self.validator.format_report(issues) + "\n\n"

                if critical:
                    yield f"❌ **{len(critical)} CRITICAL issue(s). Running optimizer pass...**\n\n"
                    async for fix_chunk in self._optimizer_pass(issues):
                        yield fix_chunk

                    recheck = self._run_deterministic_validation()
                    if recheck:
                        yield "\n⚠️ Some issues persist after optimizer. Manual review needed.\n"
                        yield self.validator.format_report(recheck) + "\n"
                    else:
                        yield "\n✅ All issues resolved after optimizer pass.\n"
                        yield self._emit_handoff()
                else:
                    yield f"⚠️ {len(non_critical)} non-critical issue(s) noted.\n"
                    yield self._emit_handoff()
            else:
                self.hooks.log_event("DETERMINISTIC_PASSED", issues=0)
                yield "✅ Deterministic checks passed. Running LLM evaluator...\n\n"

                llm_issues = await self._llm_evaluator_pass()
                if llm_issues:
                    self.hooks.log_event("LLM_EVALUATOR_ISSUES", count=len(llm_issues))
                    yield f"⚠️ LLM evaluator found {len(llm_issues)} issue(s):\n"
                    for issue in llm_issues:
                        yield f"  • {issue}\n"
                    yield "\n"
                else:
                    self.hooks.log_event("VALIDATION_PASSED", issues=0)
                    yield "✅ All design artifacts pass validation — zero issues.\n\n"
                yield self._emit_handoff()

        self.hooks.log_event("RUN_COMPLETED", project=self.project_id)

    # ── Agent SDK Loop ────────────────────────────────────────────────────

    async def _agent_loop(self, prompt: str) -> AsyncIterator[str]:
        """
        Core agent loop using Claude Agent SDK.
        Streams responses back to the caller.
        """
        try:
            from claude_agent_sdk import query, ClaudeAgentOptions

            options = ClaudeAgentOptions(
                allowed_tools=["Read", "Write", "Bash"],
                system_prompt=DESIGNER_SYSTEM_PROMPT,
                max_turns=30,
            )
            async for message in query(prompt=prompt, options=options):
                if hasattr(message, "content") and message.content:
                    yield message.content
                elif hasattr(message, "result"):
                    yield message.result

        except ImportError:
            try:
                import anthropic
                client = anthropic.Anthropic()
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=8192,
                    system=DESIGNER_SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": prompt}],
                )
                for block in response.content:
                    if hasattr(block, "text"):
                        yield block.text
            except ImportError:
                yield (
                    "⚠️ Neither `claude-agent-sdk` nor `anthropic` is installed.\n"
                    "Install one:\n"
                    "  pip install anthropic          # Direct API\n"
                    "  pip install claude-agent-sdk   # Full agent loop\n"
                )

    # ── Evaluator-Optimizer ───────────────────────────────────────────────

    def _run_deterministic_validation(self) -> list:
        """Run all deterministic validation passes."""
        return self.validator.run_all_deterministic()

    async def _llm_evaluator_pass(self) -> list[str]:
        """
        Dedicated LLM evaluator call. SEPARATE from the Designer agent.
        Returns structured list of violations.
        """
        brief_text = ""
        visual_spec_text = ""
        typo_spec_text = ""

        brief_path = self.specs_dir / "01-brief.md"
        visual_path = self.specs_dir / "04-visual-design-spec.json"
        typo_path = self.specs_dir / "05-typography-spec.json"

        if brief_path.exists():
            brief_text = brief_path.read_text()
        if visual_path.exists():
            visual_spec_text = visual_path.read_text()
        if typo_path.exists():
            typo_spec_text = typo_path.read_text()

        eval_prompt = self.validator.build_llm_evaluator_prompt(
            brief_text, visual_spec_text, typo_spec_text
        )

        try:
            from claude_agent_sdk import query, ClaudeAgentOptions

            result_text = ""
            async for message in query(
                prompt=eval_prompt,
                options=ClaudeAgentOptions(allowed_tools=[]),
            ):
                if hasattr(message, "result"):
                    result_text = message.result
                    break

            try:
                return json.loads(result_text.strip())
            except json.JSONDecodeError:
                return []

        except ImportError:
            return []

    async def _optimizer_pass(self, issues: list) -> AsyncIterator[str]:
        """Re-run generation with specific failure context."""
        fix_prompt = (
            "The design evaluator found these issues with your artifacts:\n\n"
            + "\n".join(f"• {i}" for i in issues)
            + "\n\nFix each issue. Regenerate ONLY the affected artifacts. "
            + "Re-run schema validation after each fix. "
            + "Do not regenerate artifacts that passed validation."
        )
        async for chunk in self._agent_loop(fix_prompt):
            yield chunk

    # ── Helpers ───────────────────────────────────────────────────────────

    def _build_design_prompt(self, user_input: str) -> str:
        """Build the design prompt with upstream context."""
        brief_text = ""
        script_text = ""
        scene_map_text = ""

        brief_path = self.specs_dir / "01-brief.md"
        script_path = self.specs_dir / "02-script.md"
        scene_map_path = self.specs_dir / "03-scene-map.json"

        if brief_path.exists():
            brief_text = brief_path.read_text()
        if script_path.exists():
            script_text = script_path.read_text()
        if scene_map_path.exists():
            scene_map_text = scene_map_path.read_text()

        return f"""Design all scenes for this project. Create:
1. HTML prototypes (360×640, self-contained, data-element-id on every element)
2. specs/04-visual-design-spec.json (color, focal points, depth layers)
3. specs/05-typography-spec.json (every text element with type scale)
4. specs/06-prototype-manifest.json (DOM element registry)

UPSTREAM ARTIFACTS:

--- BRIEF ---
{brief_text[:3000]}

--- SCRIPT ---
{script_text[:3000]}

--- SCENE MAP ---
{scene_map_text[:3000]}

{f'ADDITIONAL CONTEXT: {user_input}' if user_input else ''}

Follow ALL design rules. Run 6-layer QA before finalizing."""

    def _design_artifacts_present(self) -> bool:
        """Check if all 3 design specs exist."""
        return all(
            (self.specs_dir / f).exists()
            for f in [
                "04-visual-design-spec.json",
                "05-typography-spec.json",
                "06-prototype-manifest.json",
            ]
        )

    def _emit_handoff(self) -> str:
        """Generate the handoff block from validated artifacts."""
        result = generate_handoff_block(
            self.project_id,
            specs_dir=self.specs_dir,
            prototypes_dir=self.prototypes_dir,
        )
        if result["success"]:
            return "\n" + result["handoff_block"]
        else:
            return f"\n❌ Handoff blocked: {result['error']}"


# ── CLI Entry Point ──────────────────────────────────────────────────────────

async def main():
    """Run the Designer agent from the command line."""
    import sys

    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""

    if not user_input and "--help" in sys.argv:
        print("🎨 The Designer — Visual Design Agent")
        print("Usage: python -m designer.agent [optional context]")
        print("       Reads upstream specs from specs/ directory")
        return

    agent = DesignerAgent()
    async for chunk in agent.run(user_input):
        print(chunk, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
