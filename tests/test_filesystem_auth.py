import tempfile, os
from pathlib import Path
from src.security.filesystem_auth import FilesystemAuthorizer


def make_config(tmp, roots, exts):
    p = Path(tmp) / "auth.yaml"
    p.write_text(f"authorized:\n" + "".join(f"  - {r}\n" for r in roots) + "allowed_extensions:\n" + "".join(f"  - {e}\n" for e in exts))
    return str(p)


def test_allowed_and_denied():
    with tempfile.TemporaryDirectory() as d:
        allowed = Path(d) / "allowed"
        denied = Path(d) / "denied"
        allowed.mkdir(); denied.mkdir()
        f = allowed / "a.txt"
        f.write_text("hi")
        cfg = make_config(d, [str(allowed)], [".txt"])
        auth = FilesystemAuthorizer(cfg)
        assert auth.is_allowed_path(f) is True
        assert auth.is_allowed_path(denied / "x.txt") is False


def test_traversal_rejected():
    with tempfile.TemporaryDirectory() as d:
        allowed = Path(d) / "allowed"
        allowed.mkdir()
        cfg_path = make_config(d, [str(allowed)], [".txt"])
        auth = FilesystemAuthorizer(cfg_path)
        evil = allowed / ".." / "secret.txt"
        assert auth.is_allowed_path(evil) is False


def test_extension_filter():
    with tempfile.TemporaryDirectory() as d:
        allowed = Path(d) / "allowed"
        allowed.mkdir()
        (allowed / "a.exe").write_text("x")
        cfg = make_config(d, [str(allowed)], [".txt"])
        auth = FilesystemAuthorizer(cfg)
        assert auth.is_allowed_path(allowed / "a.exe") is False
