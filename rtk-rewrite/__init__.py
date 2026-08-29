"""Hermes plugin adapter for RTK command rewriting.

All rewrite logic lives in RTK's Rust ``rtk rewrite`` command; this module
only bridges Hermes ``pre_tool_call`` payloads to that command and fails open.
"""

import os
import shutil
import subprocess
import sys

ACCEPTED_REWRITE_RETURN_CODES = {0, 3}
EXPECTED_PASSTHROUGH_RETURN_CODES = {1, 2}
_RTK_PREFIXES = ("rtk ", ": RTK && ")
_rtk_available = None
_rtk_missing_warned = False


def register(ctx):
    """Register the Hermes pre-tool callback."""
    if not _check_rtk():
        return

    ctx.register_hook("pre_tool_call", _pre_tool_call)


def _check_rtk():
    """Return whether the rtk binary is in PATH, warning once when missing."""
    global _rtk_available, _rtk_missing_warned

    if _rtk_available is None:
        _rtk_available = shutil.which("rtk") is not None

    if not _rtk_available and not _rtk_missing_warned:
        _warn("rtk binary not found in PATH; Hermes hook not registered")
        _rtk_missing_warned = True

    return _rtk_available


def _enabled_backends():
    raw = os.getenv("RTK_HERMES_BACKENDS", "local").strip().lower()
    if not raw:
        return ("local",)
    parts = tuple(part.strip() for part in raw.split(",") if part.strip())
    return parts or ("local",)


def _current_backend(args):
    args = args or {}
    for key in ("env_type", "backend"):
        value = args.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip().lower()
    return (
        os.getenv("TERMINAL_ENV")
        or os.getenv("TERMINAL_BACKEND")
        or "local"
    ).strip().lower() or "local"


def _backend_allowed(backend):
    enabled = _enabled_backends()
    return "all" in enabled or backend in enabled


def _already_rtk(command):
    stripped = command.lstrip()
    return stripped.startswith(_RTK_PREFIXES)


def _pre_tool_call(tool_name=None, args=None, **_kwargs):
    """Rewrite mutable Hermes terminal command args when RTK provides a change."""
    try:
        if tool_name != "terminal" or not isinstance(args, dict):
            return
        if not _backend_allowed(_current_backend(args)):
            return

        command = args.get("command")
        if not isinstance(command, str) or not command.strip():
            return
        if _already_rtk(command):
            return

        try:
            result = subprocess.run(
                ["rtk", "rewrite", command],
                shell=False,
                timeout=2,
                capture_output=True,
                text=True,
            )
        except subprocess.TimeoutExpired:
            _warn("rtk rewrite timed out")
            return

        if result.returncode not in ACCEPTED_REWRITE_RETURN_CODES:
            if result.returncode not in EXPECTED_PASSTHROUGH_RETURN_CODES:
                _warn(f"rtk rewrite failed with exit {result.returncode}")
            return

        rewritten = result.stdout.strip()
        if rewritten and rewritten != command:
            args["command"] = rewritten
    except Exception as exc:
        _warn(type(exc).__name__)
        return


def _warn(message):
    print(f"rtk: hermes plugin warning: {message}", file=sys.stderr)


def _self_check():
    assert _already_rtk("rtk git status")
    assert _already_rtk("  : RTK && rtk ls")
    assert not _already_rtk("git status")
    assert _current_backend({"env_type": "docker"}) == "docker"
    assert _current_backend({"command": "ls"}) == "local"
    os.environ["RTK_HERMES_BACKENDS"] = "local"
    assert _backend_allowed("local")
    assert not _backend_allowed("ssh")
    os.environ["RTK_HERMES_BACKENDS"] = "all"
    assert _backend_allowed("docker")
    del os.environ["RTK_HERMES_BACKENDS"]
    skipped = {"command": "git status", "env_type": "ssh"}
    _pre_tool_call(tool_name="terminal", args=skipped)
    assert skipped["command"] == "git status"
    prefixed = {"command": "rtk git status"}
    _pre_tool_call(tool_name="terminal", args=prefixed)
    assert prefixed["command"] == "rtk git status"
    print("rtk-rewrite self-check ok")


if __name__ == "__main__":
    _self_check()
