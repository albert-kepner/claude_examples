from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass(slots=True)
class Config:
    """Configuration derived from CLI arguments."""

    root_path: Path
    dry_run: bool = False

    # Phase 3 options
    exclude: List[str] = field(default_factory=list)
    max_depth: int | None = None
    include_hidden: bool = False

    allow_dirty: bool = False

    quiet: bool = False
    verbose: bool = False


