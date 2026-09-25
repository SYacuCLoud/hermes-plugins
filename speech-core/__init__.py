"""Inject caveman, i-have-adhd, and ponytail skill text into each chat turn."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

_SKILLS = (
    ("caveman", ("caveman", "productivity/caveman"), "CAVEMAN MODE ACTIVE — level: lite"),
    ("i-have-adhd", ("i-have-adhd",), "ADHD MODE ACTIVE"),
    ("ponytail", ("ponytail", "productivity/ponytail"), "PONYTAIL MODE ACTIVE — level: full"),
)

# Appended after the skill bodies. Does not replace them.
_KOREAN = """\
KOREAN SPEECH CORRECTION

The skill bodies above stay. This note does not replace them. When they conflict on Korean grammar or sentence endings, this note wins. Other rules in those bodies stay.

When writing Korean: answer in complete 해요체 sentences. Keep particles. Do not mix 합니다체. Do not calque English into broken Korean. Do not drop reasons, conditions, or exceptions to shorten. Do not announce this style.
"""


def _homes() -> list[Path]:
    homes: list[Path] = []
    try:
        from hermes_constants import get_hermes_home

        homes.append(Path(get_hermes_home()))
    except Exception:
        env = os.environ.get("HERMES_HOME", "").strip()
        if env:
            homes.append(Path(env))
    homes.append(Path.home() / "AppData" / "Local" / "hermes")
    unique: list[Path] = []
    seen: set[str] = set()
    for home in homes:
        key = str(home)
        if key not in seen:
            seen.add(key)
            unique.append(home)
    return unique


def _strip_frontmatter(text: str) -> str:
    return re.sub(r"^---[\s\S]*?---\s*", "", text, count=1).strip()


def _skill_body(relatives: tuple[str, ...]) -> str:
    for home in _homes():
        for relative in relatives:
            path = home / "skills" / relative / "SKILL.md"
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            return _strip_frontmatter(text)
    return ""


def build_injected_context() -> str:
    parts: list[str] = []
    missing: list[str] = []
    for name, relatives, header in _SKILLS:
        body = _skill_body(relatives)
        if not body:
            missing.append(name)
            continue
        parts.append(f"{header}\n\n{body}")
    loaded = bool(parts)
    if missing:
        parts.append("Skill injection missing: " + ", ".join(missing))
    if loaded:
        parts.append(_KOREAN.strip())
    return "\n\n".join(parts)


def _pre_llm_call(**_: Any) -> dict[str, str]:
    return {"context": build_injected_context()}


def register(ctx: Any) -> None:
    ctx.register_hook("pre_llm_call", _pre_llm_call)


if __name__ == "__main__":
    text = build_injected_context()
    assert "Respond terse like smart caveman" in text
    assert "The reader has ADHD" in text
    assert "You are a lazy senior developer" in text
    assert "Skill injection missing" not in text
    assert "KOREAN SPEECH CORRECTION" in text
    assert "해요체" in text
    assert "SPEECH CORE ACTIVE" not in text
    assert text.index("You are a lazy senior developer") < text.index("KOREAN SPEECH CORRECTION")
    assert _pre_llm_call()["context"] == text
    print("ok", len(text))

