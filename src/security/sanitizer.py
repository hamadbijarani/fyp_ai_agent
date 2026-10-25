"""Treat retrieved content as untrusted; strip obvious injection attempts (defense in depth)."""

from __future__ import annotations

import re

_INJECTION_PATTERNS = [
    re.compile(r"ignore (all|previous|above) instructions", re.I),
    re.compile(r"system prompt", re.I),
    re.compile(r"you are now", re.I),
    re.compile(r"disregard", re.I),
]


def sanitize_text(text: str) -> str:
    # We do not delete content; mark suspicious lines.
    lines = text.splitlines()
    out = []
    for line in lines:
        if any(p.search(line) for p in _INJECTION_PATTERNS):
            out.append(f"[FILTERED SUSPICIOUS LINE]: {line}")
        else:
            out.append(line)
    return "\n".join(out)
