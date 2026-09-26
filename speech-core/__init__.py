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


def _home() -> Path:
    """Active profile home only, so a profile never borrows another profile's skills."""
    try:
        from hermes_constants import get_hermes_home

        return Path(get_hermes_home())
    except Exception:
        pass
    env = os.environ.get("HERMES_HOME", "").strip()
    if env:
        return Path(env)
    local = os.environ.get("LOCALAPPDATA", "").strip()
    if os.name == "nt" and local:
        return Path(local) / "hermes"
    return Path.home() / ".hermes"


def _strip_frontmatter(text: str) -> str:
    return re.sub(r"^---[\s\S]*?---\s*", "", text, count=1).strip()


def _skipped() -> set[str]:
    """Profile-local names to leave out. One name per line. Missing file = inject all."""
    path = _home() / "speech-core.skip"
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError:
        return set()
    return {line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")}


def _skill_body(relatives: tuple[str, ...]) -> str:
    skills = _home() / "skills"
    for relative in relatives:
        try:
            text = (skills / relative / "SKILL.md").read_text(encoding="utf-8-sig")
        except OSError:
            continue
        return _strip_frontmatter(text)
    return ""


def build_injected_context() -> str:
    parts: list[str] = []
    missing: list[str] = []
    skipped = _skipped()
    for name, relatives, header in _SKILLS:
        if name in skipped:
            continue
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


def build_reminder() -> str:
    """Later turns: one header line per active skill, then the Korean note.

    Hook context is replayed with each past user message, so the first turn's full
    bodies stay in history. Re-sending them every turn only duplicates tokens.
    """
    skipped = _skipped()
    names = [header for name, relatives, header in _SKILLS if name not in skipped and _skill_body(relatives)]
    if not names:
        return ""
    suffix = " — full rules were injected on the first turn and still apply."
    return "\n".join(n + suffix for n in names) + "\n\n" + _KOREAN.strip()


def _texts(messages: Any) -> list[str]:
    """User-visible and API-bound text of past messages (str or multimodal parts)."""
    out: list[str] = []
    for msg in messages or ():
        if not isinstance(msg, dict):
            continue
        for key in ("api_content", "content"):
            value = msg.get(key)
            if isinstance(value, str):
                out.append(value)
            elif isinstance(value, list):
                out.extend(p.get("text", "") for p in value if isinstance(p, dict))
    return out


def _bodies_in_history(messages: Any) -> bool:
    """True only if every active skill body still sits in the context.

    Compression can summarize away the first turn, so is_first_turn alone is not proof.
    Each body's opening is the marker: the short reminder never contains it.
    """
    skipped = _skipped()
    markers = [b[:200] for n, r, _ in _SKILLS if n not in skipped and (b := _skill_body(r))]
    if not markers:
        return True
    texts = _texts(messages)
    return all(any(m in t for t in texts) for m in markers)


def _pre_llm_call(is_first_turn: bool = True, conversation_history: Any = None, **_: Any) -> dict[str, str]:
    if is_first_turn or not _bodies_in_history(conversation_history):
        return {"context": build_injected_context()}
    return {"context": build_reminder()}


def register(ctx: Any) -> None:
    ctx.register_hook("pre_llm_call", _pre_llm_call)


if __name__ == "__main__":
    text = build_injected_context()
    if "caveman" in _skipped():
        assert "Respond terse like smart caveman" not in text
        assert "Skill injection missing" not in text or "caveman" not in text.split("Skill injection missing", 1)[-1]
    else:
        assert "Respond terse like smart caveman" in text
    assert "The reader has ADHD" in text
    assert "You are a lazy senior developer" in text
    assert "Skill injection missing" not in text
    assert "KOREAN SPEECH CORRECTION" in text
    assert "해요체" in text
    assert "SPEECH CORE ACTIVE" not in text
    assert text.index("You are a lazy senior developer") < text.index("KOREAN SPEECH CORRECTION")
    assert _pre_llm_call()["context"] == text
    assert _pre_llm_call(is_first_turn=True)["context"] == text
    kept = [{"role": "user", "content": "hi", "api_content": "hi\n\n" + text}]
    short = _pre_llm_call(is_first_turn=False, conversation_history=kept)["context"]
    assert "ADHD MODE ACTIVE" in short and "KOREAN SPEECH CORRECTION" in short
    assert "The reader has ADHD" not in short and len(short) < 1000
    heads = short.split("\n\n", 1)[0].splitlines()
    assert heads and all(h.endswith("still apply.") for h in heads)
    # Compression dropped the first turn: only a summary and reminders remain.
    lost = [{"role": "user", "content": "[summary]"}, {"role": "user", "content": "x", "api_content": "x\n\n" + short}]
    assert _pre_llm_call(is_first_turn=False, conversation_history=lost)["context"] == text
    assert _pre_llm_call(is_first_turn=False, conversation_history=None)["context"] == text
    print("ok", len(text), len(short))

