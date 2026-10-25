import tempfile
from src.storage.audit_log import AuditLog


def test_audit_record_recent():
    with tempfile.TemporaryDirectory() as d:
        log = AuditLog(db_path=f"{d}/audit.db")
        log.record("message_detected", {"id": "1"})
        rows = log.recent(10)
        assert len(rows) == 1
        assert rows[0]["event_type"] == "message_detected"
