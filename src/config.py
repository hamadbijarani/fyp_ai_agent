import os
from pathlib import Path

import yaml


def load_settings(path: str = "config/settings.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    # env overrides
    cfg.setdefault("llm", {})
    cfg["llm"]["base_url"] = os.getenv("OLLAMA_BASE_URL", cfg["llm"].get("base_url"))
    cfg["llm"]["model"] = os.getenv("OLLAMA_MODEL", cfg["llm"].get("model"))
    cfg["app"]["data_dir"] = os.getenv("DATA_DIR", cfg["app"].get("data_dir", "./data"))
    return cfg


def load_authorized_folders(path: str = "config/authorized_folders.yaml") -> dict:
    p = Path(path)
    if not p.exists():
        return {"authorized": [], "allowed_extensions": [".txt", ".pdf", ".docx", ".md"]}
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
