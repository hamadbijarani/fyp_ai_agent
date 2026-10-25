from __future__ import annotations

from pathlib import Path

import yaml


class FilesystemAuthorizer:
    def __init__(self, config_path: str = "config/authorized_folders.yaml"):
        self.config_path = config_path
        self._load()

    def _load(self):
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f) or {}
        except FileNotFoundError:
            cfg = {"authorized": [], "allowed_extensions": []}
        self.roots = [Path(p).expanduser().resolve() for p in cfg.get("authorized", [])]
        self.allowed_exts = set(cfg.get("allowed_extensions", []))

    def reload(self):
        self._load()

    def is_allowed_path(self, path: str | Path) -> bool:
        try:
            p = Path(path).expanduser().resolve(strict=False)
        except Exception:
            return False
        # reject traversal attempts already resolved; ensure not escaping via symlink
        if not p.exists():
            # allow validation of non-existent? For safety require existence for file reads
            pass
        # extension check
        if self.allowed_exts and p.suffix.lower() not in self.allowed_exts:
            return False
        for root in self.roots:
            try:
                p.relative_to(root)
                # ensure root itself allowed and path under it
                return True
            except ValueError:
                continue
        return False

    def validate(self, path: str | Path) -> Path:
        p = Path(path).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(str(p))
        if not self.is_allowed_path(p):
            raise PermissionError(f"Access denied: {p}")
        return p

    def list_allowed_files(self) -> list[Path]:
        out = []
        for root in self.roots:
            if not root.exists():
                continue
            for p in root.rglob("*"):
                if p.is_file() and (not self.allowed_exts or p.suffix.lower() in self.allowed_exts):
                    out.append(p)
        return out
