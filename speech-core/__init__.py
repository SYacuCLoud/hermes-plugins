"""Inject caveman, i-have-adhd, and ponytail skill text into each chat turn."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

# name, skill dirs, header label, default level (None = skill has no levels), allowed levels
_SKILLS = (
    ("caveman", ("caveman", "productivity/caveman"), "CAVEMAN", "lite",
     {"lite", "full", "ultra", "wenyan-lite", "wenyan-full", "wenyan-ultra"}),
    ("i-have-adhd", ("i-have-adhd",), "ADHD", None, set()),
    ("ponytail", ("ponytail", "productivity/ponytail"), "PONYTAIL", "full", {"lite", "full", "ultra"}),
)
_NAMES = tuple(s[0] for s in _SKILLS)

# Off switches the skill bodies themselves define. Matched only as a whole line,
# so a message that quotes or discusses the commands does not trigger them.
_STOP = {
    "normal mode": _NAMES,
    "stop caveman": ("caveman",),
    "stop adhd mode": ("i-have-adhd",),
    "stop ponytail": ("ponytail",),
}
_LEVEL_CMD = re.compile(r"/(caveman|ponytail)\s+([a-z-]+)")

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


_FRONTMATTER = re.compile(r"---[ \t]*\r?\n.*?\r?\n---[ \t]*(?:\r?\n|$)", re.S)


def _strip_frontmatter(text: str) -> str:
    """Drop YAML frontmatter; both fences must be lines of their own."""
    m = _FRONTMATTER.match(text)
    return (text[m.end():] if m else text).strip()


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


def _parts_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(p.get("text", "") for p in value if isinstance(p, dict))
    return ""


def _sent_texts(messages: Any) -> list[str]:
    """What the model actually saw: a non-empty api_content wins over content, as in Hermes."""
    out: list[str] = []
    for msg in messages or ():
        if not isinstance(msg, dict):
            continue
        api = msg.get("api_content")
        out.append(api if isinstance(api, str) and api else _parts_text(msg.get("content")))
    return out


def _user_texts(messages: Any, user_message: Any) -> list[str]:
    """What the user typed, oldest first. content is the clean text; api_content carries injections."""
    out = [_parts_text(m.get("content")) for m in messages or () if isinstance(m, dict) and m.get("role") == "user"]
    current = _parts_text(user_message)
    if current and (not out or out[-1] != current):
        out.append(current)
    return out


def _mode_state(messages: Any = None, user_message: Any = None) -> dict[str, str | None]:
    """name -> level ("" for level-less skills) when on, None when the user turned it off.

    ponytail: state lives only in the chat history. If compression drops the command,
    the mode falls back to its default. Persist per session if that bites.
    """
    state: dict[str, str | None] = {name: (default or "") for name, _, _, default, _ in _SKILLS}
    levels = {name: allowed for name, _, _, _, allowed in _SKILLS}
    for text in _user_texts(messages, user_message):
        for raw in text.splitlines():
            line = raw.strip().strip("`\"'").rstrip(".!").strip().lower()
            if line in _STOP:
                for name in _STOP[line]:
                    state[name] = None
                continue
            m = _LEVEL_CMD.fullmatch(line)
            if m:
                name, level = m.groups()
                if level == "off":
                    state[name] = None
                elif level in levels[name]:
                    state[name] = level
    return state


def _active(state: dict[str, str | None]) -> tuple[list[tuple[str, str]], list[str]]:
    """(header, body) for skills on, labels for skills off. Skipped/uninstalled skills are neither."""
    on: list[tuple[str, str]] = []
    off: list[str] = []
    skipped = _skipped()
    for name, relatives, label, _, _ in _SKILLS:
        if name in skipped:
            continue
        body = _skill_body(relatives)
        if not body:
            continue
        level = state[name]
        if level is None:
            off.append(label)
        else:
            on.append((f"{label} MODE ACTIVE" + (f" — level: {level}" if level else ""), body))
    return on, off


def _off_lines(off: list[str]) -> list[str]:
    return [f"{label} MODE OFF — the user turned it off. Ignore its rules until they turn it back on." for label in off]


def build_injected_context(state: dict[str, str | None] | None = None) -> str:
    state = state or _mode_state()
    on, off = _active(state)
    skipped = _skipped()
    missing = [n for n, r, *_ in _SKILLS if n not in skipped and state[n] is not None and not _skill_body(r)]
    parts = [f"{header}\n\n{body}" for header, body in on]
    if missing:
        parts.append("Skill injection missing: " + ", ".join(missing))
    parts += _off_lines(off)
    if on:
        parts.append(_KOREAN.strip())
    return "\n\n".join(parts)


def build_reminder(state: dict[str, str | None] | None = None) -> str:
    """Later turns: one header line per active skill, then the Korean note.

    Hook context is replayed with each past user message, so the full bodies stay in
    history. Re-sending them every turn only duplicates tokens.
    """
    on, off = _active(state or _mode_state())
    lines = [h + " — full rules were injected earlier and still apply." for h, _ in on] + _off_lines(off)
    if not lines:
        return ""
    return "\n".join(lines) + ("\n\n" + _KOREAN.strip() if on else "")


def _bodies_in_history(messages: Any, state: dict[str, str | None] | None = None) -> bool:
    """True only if every active skill body still sits whole in what the model was sent.

    Compression can summarize or truncate the first turn, so is_first_turn alone is not proof,
    and a surviving prefix is not proof that the conditions and exceptions survived.
    """
    on, _ = _active(state or _mode_state(messages))
    if not on:
        return True
    texts = _sent_texts(messages)
    return all(any(body in t for t in texts) for _, body in on)


def _pre_llm_call(
    is_first_turn: bool = True, conversation_history: Any = None, user_message: Any = None, **_: Any
) -> dict[str, str]:
    state = _mode_state(conversation_history, user_message)
    if is_first_turn or not _bodies_in_history(conversation_history, state):
        return {"context": build_injected_context(state)}
    return {"context": build_reminder(state)}


def register(ctx: Any) -> None:
    ctx.register_hook("pre_llm_call", _pre_llm_call)


if __name__ == "__main__":
    text = build_injected_context()
    if "caveman" in _skipped():
        assert "Respond terse like smart caveman" not in text and "CAVEMAN MODE" not in text
    else:
        assert "Respond terse like smart caveman" in text
    assert "The reader has ADHD" in text
    assert "You are a lazy senior developer" in text
    assert "Skill injection missing" not in text
    assert "KOREAN SPEECH CORRECTION" in text and "해요체" in text
    assert text.index("You are a lazy senior developer") < text.index("KOREAN SPEECH CORRECTION")
    assert _pre_llm_call()["context"] == text
    assert _pre_llm_call(is_first_turn=True)["context"] == text

    def turn(history: list, msg: str) -> str:
        return _pre_llm_call(is_first_turn=False, conversation_history=history, user_message=msg)["context"]

    kept = [{"role": "user", "content": "hi", "api_content": "hi\n\n" + text}]
    short = turn(kept, "next")
    assert "ADHD MODE ACTIVE" in short and "KOREAN SPEECH CORRECTION" in short
    assert "The reader has ADHD" not in short and len(short) < 1000
    heads = short.split("\n\n", 1)[0].splitlines()
    assert heads and all(h.endswith("still apply.") for h in heads)

    # Off and level commands, in the current message and remembered from history.
    s = turn(kept, "stop adhd mode")
    assert "ADHD MODE OFF" in s and "ADHD MODE ACTIVE" not in s and "PONYTAIL MODE ACTIVE — level: full" in s
    s = turn(kept, "stop ponytail")
    assert "PONYTAIL MODE OFF" in s and "PONYTAIL MODE ACTIVE" not in s and "ADHD MODE ACTIVE" in s
    s = turn(kept, "Normal mode.")
    assert "ACTIVE" not in s and "KOREAN SPEECH CORRECTION" not in s and "ADHD MODE OFF" in s
    assert "PONYTAIL MODE ACTIVE — level: lite" in turn(kept, "/ponytail lite")
    assert "PONYTAIL MODE ACTIVE — level: ultra" in turn(kept, "/ponytail ultra")
    assert "PONYTAIL MODE OFF" in turn(kept, "/ponytail off")
    later = kept + [{"role": "assistant", "content": "ok"}, {"role": "user", "content": "/ponytail ultra"}]
    assert "level: ultra" in turn(later, "next")
    back = later + [{"role": "user", "content": "normal mode"}, {"role": "user", "content": "/ponytail lite"}]
    s = turn(back, "next")
    assert "PONYTAIL MODE ACTIVE — level: lite" in s and "ADHD MODE OFF" in s
    # Quoting the commands inside a sentence does not trigger them; unknown levels are ignored.
    assert "OFF" not in turn(kept, "I tested stop adhd mode, stop ponytail, normal mode")
    assert "level: full" in turn(kept, "/ponytail bogus")

    # Only a 200-char prefix of each body survived: re-inject the full bodies.
    stub = "\n".join(b[:200] for _, b in _active(_mode_state())[0])
    assert turn([{"role": "user", "content": "x", "api_content": stub}], "y") == text
    # Full body only in the display content, not in what was sent: re-inject.
    assert turn([{"role": "user", "content": text, "api_content": "summary"}], "y") == text
    # Compression dropped the first turn: only a summary and reminders remain.
    lost = [{"role": "user", "content": "[summary]"}, {"role": "user", "content": "x", "api_content": "x\n\n" + short}]
    assert turn(lost, "y") == text
    assert _pre_llm_call(is_first_turn=False, conversation_history=None)["context"] == text

    # Frontmatter fences must be whole lines.
    fm = "---\nname: x\ndescription: before --- after\n---\nBODY\n---\nmore"
    assert _strip_frontmatter(fm) == "BODY\n---\nmore"
    assert _strip_frontmatter("---\r\nname: x\r\n---\r\nBODY") == "BODY"
    assert _strip_frontmatter("no frontmatter --- here") == "no frontmatter --- here"
    print("ok", len(text), len(short))
