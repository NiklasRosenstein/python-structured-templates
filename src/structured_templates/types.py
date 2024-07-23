from typing import Any, TypeVar


Value = dict[str, Any] | list[Any] | str | int | float | bool | None
T_Value = TypeVar("T_Value", bound=Value)
