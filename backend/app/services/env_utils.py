from __future__ import annotations

"""Helpers for reading local .env files without external dependencies."""

from pathlib import Path
from typing import Optional


def read_env_key(name: str) -> Optional[str]:
    """Return a value from backend/.env if present."""
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return None
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.lstrip("\ufeff").strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == name:
            return value.strip().strip('"').strip("'")
    return None
