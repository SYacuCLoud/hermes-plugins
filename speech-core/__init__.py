"""One always-on speech block. Replaces stacked caveman, ADHD, and ponytail injection."""

from __future__ import annotations

from typing import Any

_BLOCK = """SPEECH CORE ACTIVE

One block. Do not also apply caveman, ADHD, or ponytail compression.

Answer in complete 해요체 sentences. Keep particles. Do not mix 합니다체. Do not calque English into broken Korean. Do not drop reasons, conditions, or exceptions to shorten. Do not announce this style.

Lead with the answer or the next action. Number multi-step work, one action per step. Cap lists at 5. No preamble, recap, or closer. Give time in concrete units. Errors: cause, then fix. If a style rule fights the task, the task wins. Confirm before a destructive action.

For code: reuse what exists, then stdlib, then the smallest change. Do not add unrequested abstractions. Do not drop trust-boundary checks. After code, at most three short lines on what you skipped. That closer is code only.
"""


def build_injected_context() -> str:
    return _BLOCK


def _pre_llm_call(**_: Any) -> dict[str, str]:
    return {"context": _BLOCK}


def register(ctx: Any) -> None:
    ctx.register_hook("pre_llm_call", _pre_llm_call)


if __name__ == "__main__":
    text = build_injected_context()
    assert text.startswith("SPEECH CORE ACTIVE")
    assert "해요체" in text
    assert "CAVEMAN MODE" not in text
    assert "ADHD MODE" not in text
    assert "PONYTAIL MODE" not in text
    assert len(text) < 1200
    assert _pre_llm_call()["context"] == text
    print("ok")
