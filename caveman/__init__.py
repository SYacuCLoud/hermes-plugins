"""Always-on caveman mode via pre_llm_call."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

DEFAULT_MODE = "lite"
MODES = {"off", "lite", "full", "ultra", "wenyan-lite", "wenyan-full", "wenyan-ultra"}
SKILL_CANDIDATES = [
    Path(__file__).resolve().parent / "skills" / "caveman" / "SKILL.md",
    Path(r"C:\_AX\shared-skills\caveman\SKILL.md"),
    Path.home() / "_AX" / "shared-skills" / "caveman" / "SKILL.md",
]

_current_mode: str | None = None


def _mode(raw: str | None) -> str | None:
    if not isinstance(raw, str):
        return None
    value = raw.strip().lower()
    return value if value in MODES else None


def _skill_text() -> str:
    for path in SKILL_CANDIDATES:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        return re.sub(r"^---[\s\S]*?---\s*", "", text, count=1)
    return (
        "Respond terse like smart caveman. All technical substance stay. "
        "Only fluff die. Off only: stop caveman / normal mode."
    )


def build_injected_context(mode: str | None = None) -> str:
    effective = _mode(mode) or _current_mode or DEFAULT_MODE
    if effective == "off":
        return ""
    return f"CAVEMAN MODE ACTIVE — level: {effective}\n\n{_skill_text()}"


def _pre_llm_call(**_: Any) -> dict[str, str] | None:
    context = build_injected_context()
    return {"context": context} if context else None


def _handle_mode_command(raw_args: str) -> str:
    global _current_mode
    arg = (raw_args or "").strip().lower()
    if not arg:
        return f"Caveman mode: {_current_mode or DEFAULT_MODE}. Use `/caveman lite|full|ultra|off`."
    mode = _mode(arg)
    if not mode:
        return "Usage: /caveman [lite|full|ultra|wenyan-lite|wenyan-full|wenyan-ultra|off]"
    _current_mode = mode
    return f"Caveman mode set to {mode}."


def register(ctx: Any) -> None:
    ctx.register_hook("pre_llm_call", _pre_llm_call)
    ctx.register_command(
        "caveman",
        _handle_mode_command,
        description="Set caveman speech mode: lite, full, ultra, or off.",
        args_hint="[lite|full|ultra|off]",
    )
