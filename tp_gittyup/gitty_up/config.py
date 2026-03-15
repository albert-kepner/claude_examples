from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Config:
    """Configuration derived from CLI arguments."""

    root_path: Path
    dry_run: bool = False

