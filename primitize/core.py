from copy import deepcopy
from dataclasses import Field, field, fields, is_dataclass
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar

from typing_extensions import Protocol


class Dataclass(Protocol):
    __dataclass_fields__: Dict


FieldValue = TypeVar("FieldValue")


def primitized(
    rename: Optional[str] = None,
    unset_if_empty: bool = False,
    modifier: Callable[[FieldValue, Dataclass], Any] = lambda v, o: v,
    validator: Callable[[FieldValue, Dataclass], Tuple[bool, str]] = lambda v, o: (True, ""),
    writer: Optional[Callable[[FieldValue, Dataclass], None]] = None,
    metadata: Dict[str, Any] = None,
    **kwargs,
) -> Field:
    """Overload of dataclass.field.

    There is a couple more attributes to add metadata specific to tpl8tr:
    * rename: Name used for the key representing this field when serializing.
    * unset_if_empty: Whether the field is added or not when the value it empty.
    * modifier: Function to replace the value, useful for reformating.
    * validator: Function returning whether the value is valid or not and why.
    * writer: Function to write the value out to some file. Note that if a value
              is written, it is not part of the resulting object.

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
    _meta["writer"] = writer

    return field(metadata=metadata, **kwargs)


def primitize(obj: Dataclass) -> Dict[str, Any]:
    result = {}
    _defaults = primitized().metadata["primitize"]
    for field_meta in fields(obj):
        ctx = deepcopy(obj)
        _meta = {}
        _meta.update(_defaults)
        _meta.update(field_meta.metadata.get("primitize", {}))

        value = getattr(obj, field_meta.name)
        value = _meta["modifier"](value, ctx)
        if is_dataclass(value):
            value = primitize(value)

        is_valid, error_msg = _meta["validator"](deepcopy(value), ctx)
        assert is_valid, f"Object `{value}` failed validation: `{error_msg}`"

        if _meta.get("unset_if_empty", False):
            if hasattr(value, "__len__") and len(value) == 0:
                continue  # Skipping this field because it is empty
            if value is None:
                continue  # Skipping this field it is empty

        if _meta["writer"] is None:
            result[_meta["rename"] or field_meta.name] = value
        else:
            _meta["writer"](value, ctx)
    return result
