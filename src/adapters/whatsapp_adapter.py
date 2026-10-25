"""WhatsApp adapter: controlled test-data importer (no paid API) for v1."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.adapters.message_schema import Message


def normalize_record(raw: dict[str, Any]) -> Message:
    ts = raw.get("timestamp")
    if isinstance(ts, (int, float)):
        dt = datetime.fromtimestamp(ts)
    elif isinstance(ts, str):
        dt = datetime.fromisoformat(ts)
    else:
        dt = datetime.now()
    return Message(
        id=str(raw.get("id", "")),
        source="whatsapp",
        sender=raw.get("sender", raw.get("from", "")),
        timestamp=dt,
        subject=None,
        body=raw.get("body", raw.get("text", "")),
        metadata={k: v for k, v in raw.items() if k not in {"id", "sender", "from", "timestamp", "body", "text"}},
    )


class WhatsAppImporter:
    def load_jsonl(self, path: str | Path) -> list[Message]:
        out = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                out.append(normalize_record(json.loads(line)))
        return out

    def load_json(self, path: str | Path) -> list[Message]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return [normalize_record(r) for r in data]
        return [normalize_record(data)]
