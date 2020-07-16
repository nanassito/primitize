import logging
from copy import deepcopy
from dataclasses import Field, dataclass, field, fields, is_dataclass
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar, Union

from typing_extensions import Protocol


class Dataclass(Protocol):
    __dataclass_fields__: Dict


FieldValue = TypeVar("FieldValue")
_LOG = logging.getLogger(__name__)
T = TypeVar("T")


def primitized(
    rename: Optional[str] = None,
    unset_if_empty: bool = False,
    modifier: Callable[[Dataclass, FieldValue], Any] = lambda self, value: value,
    validator: Callable[
        [Dataclass, FieldValue], Tuple[bool, str]
    ] = lambda self, value: (True, ""),
    # DeprecationWarning: Replaced with defining a `primitize()` method on the object
    writer: Any = None,
    metadata: Dict[str, Any] = None,
    **kwargs,
) -> Field:
    """Overload of dataclass.field.

    There is a couple more attributes to add metadata specific to tpl8tr:
    * rename: Name used for the key representing this field when serializing.
    * unset_if_empty: Whether the field is added or not when the value it empty.
    * modifier: Function to replace the value, useful for reformating.
    * validator: Function returning whether the value is valid or not and why.

    All functions are called with the with the field as the field's value as the
    first argument and the full object as the second argument. Modifications to
    the object are not guarantied to be taken into account.
    """
    metadata = metadata or {}
    metadata.setdefault("primitize", {})
    _meta = metadata["primitize"]

    _meta["rename"] = rename
    _meta["unset_if_empty"] = unset_if_empty
    _meta["modifier"] = modifier
    _meta["validator"] = validator
    assert (
        writer is None
    ), "writer() is replaced by overriding the `primitize()` method."

    return field(metadata=metadata, **kwargs)


def best_effort_deepcopy(obj: T) -> T:
    try:
        return deepcopy(obj)
    except Exception as e:
        _LOG.warn(f"Failed to deepcopy the object: {e}")
        return obj


def _default_primitize(obj: Union[Dataclass, "Primitizable"]) -> Dict[str, Any]:
    result = {}
    _defaults = primitized().metadata["primitize"]
    for field_meta in fields(obj):
        ctx = best_effort_deepcopy(obj)
        _meta = {}
        _meta.update(_defaults)
        _meta.update(field_meta.metadata.get("primitize", {}))

        value = getattr(obj, field_meta.name, None)
        value = _meta["modifier"](ctx, value)
        if is_dataclass(value):
            value = primitize(value)

        is_valid, error_msg = _meta["validator"](ctx, best_effort_deepcopy(value))
        assert is_valid, f"Object `{value}` failed validation: `{error_msg}`"

        if _meta.get("unset_if_empty", False):
            if hasattr(value, "__len__") and len(value) == 0:
                continue  # Skipping this field because it is empty
            if value is None:
                continue  # Skipping this field it is empty

        result[_meta["rename"] or field_meta.name] = value
    return result


@dataclass
class Primitizable:
    def primitize(self: "Primitizable") -> Dict[str, Any]:
        return _default_primitize(self)


def primitize(obj: Any) -> Dict[str, Any]:
    if hasattr(obj, "primitize"):
        return obj.primitize()
    else:
        return _default_primitize(obj)
