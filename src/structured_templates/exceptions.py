from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from structured_templates.context import Context


@dataclass
class TemplateError(Exception):
    """
    Raised for errors during template evaluation.
    """

    ctx: Context
    message: str

    def __str__(self) -> str:
        return f"at {self.ctx.format_location()}: {self.message}"
