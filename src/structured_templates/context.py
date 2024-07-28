from __future__ import annotations
from collections import ChainMap
from dataclasses import dataclass, field
from typing import Any, Generic

from structured_templates.types import T_Value
from structured_templates.exceptions import TemplateError


@dataclass
class Context(Generic[T_Value]):
    """
    A context object holds a value for processing in the template with additional contextual information, such
    as the parent context and key from which the value was retrieved.
    """

    parent: Context | None = field(repr=False)
    """ The parent context. """

    key: str | int | None
    """ The name of the key in the parent context that this context was retrieved from. Must be set if [parent] is. """

    data: T_Value
    """ The data of the context. """

    scope: dict[str, Any] | None = field(default_factory=dict)
    """ Variables that are available to expressions in this context. """

    def __post_init__(self) -> None:
        assert self.parent is None or self.key is not None, "The key must be provided if the parent is provided."

    def error(self, message: str) -> "TemplateError":
        """
        Create a template error for the context.
        """

        return TemplateError(self, message)

    def format_location(self) -> str:
        """
        Format the context location for human readability.
        """

        if self.parent is None:
            return "$"
        else:
            assert self.key is not None
            if isinstance(self.key, int) or (isinstance(self.key, str) and self.key.isidentifier()):
                return f"{self.parent.format_location()}.{self.key}"
            else:
                return f"{self.parent.format_location()}.'{self.key}'"

    def full_scope(self, globals_: dict[str, Any] | None = None) -> ChainMap:
        """
        Create a ChainMap of the scope.
        """

        maps = []

        if globals_ is not None:
            maps.append(globals_)

        curr: Context | None = self
        while curr:
            if curr.scope:
                maps.append(curr.scope)
            curr = curr.parent

        return ChainMap(*maps)
