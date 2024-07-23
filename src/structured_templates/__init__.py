from collections import ChainMap
from collections.abc import Iterable
from dataclasses import dataclass, field
import re
from typing import Any, Generic, TypeVar, cast


Value = dict[str, Any] | list[Any] | str | int | float | bool | None
T_Value = TypeVar("T_Value", bound=Value)


class TemplateEngine:
    """
    Template engine for structured templates.
    """

    @dataclass
    class Context(Generic[T_Value]):
        """
        Context for the template engine that holds the data and traces the evaluation.
        """

        parent: "TemplateEngine.Context | None" = field(repr=False)
        key: str | None
        data: T_Value
        scope: dict[str, Any] | None = field(default_factory=dict)

        def __post_init__(self) -> None:
            assert self.parent is None or self.key is not None, "The key must be provided if the parent is provided."

        def trace_location(self) -> str:
            """
            Trace the location of the context.
            """

            if self.parent is None:
                return "$"
            else:
                assert self.key is not None
                if self.key.isdigit() or self.key.isidentifier():
                    return f"{self.parent.trace_location()}.{self.key}"
                else:
                    return f"{self.parent.trace_location()}.'{self.key}'"

        def error(self, message: str) -> "TemplateError":
            """
            Create a template error for the context.
            """

            return TemplateError(self, message)

        def scope_chainmap(self, globals_: dict[str, Any] | None = None) -> ChainMap:
            """
            Create a ChainMap of the scope.
            """

            return ChainMap(self.scope or {}, self.parent.scope_chainmap(globals_) if self.parent else (globals_ or {}))

    def __init__(self, globals_: dict[str, Any] | None = None):
        self.globals = globals_ or {}

    def evaluate(self, value: Value | Context[Value]) -> Value:
        """
        Evaluate the given value.
        """

        if not isinstance(value, self.Context):
            value = self.Context(None, None, value)

        match value.data:
            case dict():
                return self.evaluate_dict(cast(TemplateEngine.Context[dict[str, Value]], value))
            case list():
                return self.evaluate_list(cast(TemplateEngine.Context[list[Value]], value))
            case str():
                return self.evaluate_string(cast(TemplateEngine.Context[str], value))
            case _:
                return value.data

    def evaluate_dict(self, ctx: Context[dict[str, Value]]) -> dict[str, Value]:
        """
        Evaluate the given dictionary.
        """

        result: dict[str, Value] = {}
        for key, value in ctx.data.items():
            subctx = self.Context(ctx, key, value)

            if key.startswith("if(") and key.endswith(")"):
                if not isinstance(value, dict):
                    raise subctx.error("The value of an if block must be a dictionary.")
                if self.evaluate_expression(self.Context(ctx, key, key[3:-1])):
                    result.update(self.evaluate_dict(self.Context(ctx, key, value)))

            elif key.startswith("for(") and key.endswith(")"):
                if not isinstance(value, dict):
                    raise subctx.error("The value of a for block must be a dictionary.")

                expr = key[4:-1]  # TODO: Better parsing of the for block syntax
                if " in " not in expr:
                    raise subctx.error(f"Invalid for block expression (missing 'in'): {expr}")

                var, iterable = expr.split(" in ")
                if not var.isidentifier():
                    raise subctx.error(f"Invalid for block variable (not an identifier): {var}")

                it = self.evaluate_expression(self.Context(ctx, key, iterable))
                if not isinstance(it, Iterable):
                    raise subctx.error(f"The iterable of a for block must be iterable, got {type(it).__name__}.")

                for idx, item in enumerate(it):
                    result.update(self.evaluate_dict(self.Context(subctx, str(idx), value, {var: item})))

            else:
                key_value = self.evaluate_string(self.Context(ctx, key, key))
                if not isinstance(key_value, str):
                    raise subctx.error(f"Expected a string key, got {type(key_value).__name__}")
                result[key_value] = self.evaluate(self.Context(ctx, key, value))

        return result

    def evaluate_list(self, ctx: Context[list[Value]]) -> list[Value]:
        """
        Evaluate the given list.
        """

        return [self.evaluate(self.Context(ctx, None, item)) for item in ctx.data]

    def evaluate_string(self, ctx: Context[str]) -> Value:
        """
        Evaluate the given string.
        """

        if ctx.data.startswith("${{") and ctx.data.endswith("}}"):
            return self.evaluate_expression(self.Context(ctx.parent, ctx.key, ctx.data[3:-2]))

        def _repl(m: re.Match[str]) -> str:
            result = self.evaluate_expression(self.Context(ctx.parent, ctx.key, m.group(1)))
            if not isinstance(result, int | float | str | bool | None):
                raise ValueError(f"Expected a plain value, got {type(result).__name__} [@ {ctx.trace_location()}]")
            return str(result) if result is not None else ""

        return re.sub(r"\$\{\{(.+?)\}\}", _repl, ctx.data)

    def evaluate_expression(self, ctx: Context[str]) -> bool:
        """
        Evaluate the given expression.
        """

        try:
            # TODO: Don't manifest full ChainMap, this is a huge performance hit.
            return eval(ctx.data, dict(ctx.scope_chainmap(self.globals)))
        except Exception as e:
            raise ctx.error(f"Failed to evaluate the expression: {e}") from e


@dataclass
class TemplateError(Exception):
    """
    Raised for errors during template evaluation.
    """

    ctx: TemplateEngine.Context
    message: str

    def __str__(self) -> str:
        return f"at {self.ctx.trace_location()}: {self.message}"
