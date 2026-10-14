"""Allow-listed, read-only analysis tools for Gamy's research coach.

No shell, filesystem traversal, network, dynamic imports, or arbitrary code tool
is exposed here. Every tool accepts structured data and returns JSON-safe output.
"""
from __future__ import annotations

from typing import Any, Callable

from .self_improvement import compare_reports, diagnose_report, make_experiment_plan, validate_report


class ToolError(ValueError):
    """Raised for unknown tools or invalid tool arguments."""


class ResearchToolbox:
    """Small explicit tool registry used by the self-improvement loop."""

    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., dict[str, Any]]] = {
            "validate_report": self.validate_report,
            "diagnose_report": self.diagnose_report,
            "make_experiment_plan": self.make_experiment_plan,
            "compare_reports": self.compare_reports,
        }

    @property
    def available_tools(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))

    def call(self, name: str, **kwargs: Any) -> dict[str, Any]:
        tool = self._tools.get(name)
        if tool is None:
            raise ToolError(f"Tool not allow-listed: {name}")
        return tool(**kwargs)

    @staticmethod
    def validate_report(*, report: dict[str, Any]) -> dict[str, Any]:
        problems = validate_report(report)
        return {"valid": not problems, "problems": problems}

    @staticmethod
    def diagnose_report(*, report: dict[str, Any]) -> dict[str, Any]:
        return diagnose_report(report)

    @staticmethod
    def make_experiment_plan(*, diagnosis: dict[str, Any]) -> dict[str, Any]:
        return make_experiment_plan(diagnosis)

    @staticmethod
    def compare_reports(*, baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
        return compare_reports(baseline, candidate)
