"""Always-on i-have-adhd output shape via pre_llm_call."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

DEFAULT_MODE = "on"
MODES = {"on", "off"}
SKILL_CANDIDATES = [
    Path(__file__).resolve().parent / "skills" / "i-have-adhd" / "SKILL.md",
    Path.home() / "AppData" / "Local" / "hermes" / "skills" / "i-have-adhd" / "SKILL.md",
]

_current_mode: str | None = None


def _mode(raw: str | None) -> str | None:
    if not isinstance(raw, str):
        return None
    value = raw.strip().lower().replace("_", "-")
    if value in {"stop", "stop adhd", "stop adhd mode", "normal", "normal mode"}:
        return "off"
    return value if value in MODES else None


def _skill_text() -> str:
    for path in SKILL_CANDIDATES:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        return re.sub(r"^---[\s\S]*?---\s*", "", text, count=1)
    return (
        "The reader has ADHD. Lead with the next action. Number multi-step work. "
        "Cap lists at 5. No preamble or closer. Off only: stop adhd mode / normal mode."
    )


def build_injected_context(mode: str | None = None) -> str:
    effective = _mode(mode) or _current_mode or DEFAULT_MODE
    if effective == "off":
        return ""
    return f"ADHD MODE ACTIVE\n\n{_skill_text()}"


def _pre_llm_call(**_: Any) -> dict[str, str] | None:
    context = build_injected_context()
    return {"context": context} if context else None


def _handle_mode_command(raw_args: str) -> str:
    global _current_mode
    arg = (raw_args or "").strip().lower()
    if not arg:
        return f"ADHD mode: {_current_mode or DEFAULT_MODE}. Use `/i-have-adhd on|off`."
    mode = _mode(arg)
    if not mode:
        return "Usage: /i-have-adhd [on|off]"
    _current_mode = mode
    return f"ADHD mode set to {mode}."


def register(ctx: Any) -> None:
    ctx.register_hook("pre_llm_call", _pre_llm_call)
    ctx.register_command(
        "i-have-adhd",
        _handle_mode_command,
        description="Set ADHD output mode: on or off.",
        args_hint="[on|off]",
    )
