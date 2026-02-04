"""PYBP rule metadata and registry. All rules have full metadata per spec §5."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, List, Optional

# Severity: info | advisory | warning only (§7)
SEVERITIES = ("info", "advisory", "warning")


@dataclass(frozen=True)
class PybpRule:
    """Metadata for one PYBP rule. No rule without complete metadata (§5)."""

    rule_id: str
    title: str
    category: str
    description: str
    rationale: str
    authority: str
    citation: str
    detection_strategy: str
    thresholds: Optional[str]
    suggestion: str
    severity: str  # info | advisory | warning
    check: Callable[[Any, str], List[dict]]  # (ast_node, source) -> list of advisory dicts

    def __post_init__(self) -> None:
        if self.severity not in SEVERITIES:
            raise ValueError(f"severity must be one of {SEVERITIES}")
