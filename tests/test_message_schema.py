from datetime import datetime
from src.adapters.message_schema import Message
from src.adapters.whatsapp_adapter import normalize_record
from src.adapters.email_adapter import normalize_gmail_message


def test_message_normalized_text():
    m = Message(id="1", source="email", sender="a@b.com", timestamp=datetime.now(), subject="Hi", body="hello")
    t = m.normalized_text()
    assert "Subject: Hi" in t and "hello" in t


def test_whatsapp_normalize():
    m = normalize_record({"id": "w1", "sender": "Bob", "timestamp": "2026-01-01T10:00:00", "body": "hey"})
    assert m.source == "whatsapp" and m.sender == "Bob"


def test_gmail_normalize():
    raw = {"id": "g1", "internalDate": "1700000000000", "payload": {"headers": [{"name": "From", "value": "x@y.com"}, {"name": "Subject", "value": "Test"}], "body": {"data": "aGVsbG8="}}}
    m = normalize_gmail_message(raw)
    assert m.source == "email" and m.subject == "Test" and "hello" in m.body
