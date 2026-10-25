"""Email adapter (Gmail API read-only). Returns normalized Message objects."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.adapters.message_schema import Message


def normalize_gmail_message(raw: dict[str, Any]) -> Message:
    headers = {h["name"].lower(): h["value"] for h in raw.get("payload", {}).get("headers", [])}
    body = _extract_body(raw.get("payload", {}))
    ts_ms = int(raw.get("internalDate", "0"))
    ts = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc) if ts_ms else datetime.now(timezone.utc)
    return Message(
        id=raw.get("id", ""),
        source="email",
        sender=headers.get("from", ""),
        timestamp=ts,
        subject=headers.get("subject"),
        body=body,
        metadata={"threadId": raw.get("threadId"), "labelIds": raw.get("labelIds", [])},
    )


def _extract_body(payload: dict[str, Any]) -> str:
    import base64

    if "parts" in payload:
        for part in payload["parts"]:
            text = _extract_body(part)
            if text:
                return text
    data = payload.get("body", {}).get("data")
    if data:
        try:
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        except Exception:
            return ""
    return payload.get("body", {}).get("text", "") or ""


class GmailAdapter:
    """Thin wrapper; network calls are optional and not invoked in tests."""

    def __init__(self, service=None):
        self.service = service

    def fetch_unread(self, max_results: int = 20) -> list[Message]:
        if self.service is None:
            raise RuntimeError("Gmail service not configured")
        res = self.service.users().messages().list(userId="me", q="is:unread", maxResults=max_results).execute()
        out = []
        for m in res.get("messages", []):
            full = self.service.users().messages().get(userId="me", id=m["id"], format="full").execute()
            out.append(normalize_gmail_message(full))
        return out
