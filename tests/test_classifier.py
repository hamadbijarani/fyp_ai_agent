from datetime import datetime
from src.adapters.message_schema import Message
from src.intent.classifier import IntentClassifier
from src.llm.schemas import ClassificationResult


class FakeClient:
    def generate_json(self, prompt, system=None):
        return {"intent": "reply_needed", "needs_reply": True, "needs_file_context": True,
                "missing_info": [], "confidence": 0.9, "rationale": "ok"}

    def generate(self, prompt, system=None, format_json=False):
        return "{}"


def test_classify_success():
    clf = IntentClassifier(client=FakeClient())
    m = Message(id="1", source="email", sender="a@b.com", timestamp=datetime.now(), body="send report")
    r = clf.classify(m)
    assert r.needs_file_context is True
    assert isinstance(r, ClassificationResult)


class BadClient:
    def generate_json(self, prompt, system=None):
        raise RuntimeError("boom")
    def generate(self, prompt, system=None, format_json=False):
        raise RuntimeError("boom")


def test_classify_fail_safe():
    clf = IntentClassifier(client=BadClient())
    m = Message(id="2", source="email", sender="a@b.com", timestamp=datetime.now(), body="x")
    r = clf.classify(m)
    assert r.needs_reply is False
    assert r.intent == "no_action"
