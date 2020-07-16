from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import Mock, call

import pytest

from primitize.core import primitize, primitized


@pytest.mark.parametrize(
    ("field_a", "field_b", "instanciation", "expected", "msg"),
    [
        (field(), field(), "A(1)", {"a": 1}, "Int - no settings"),
        (field(), field(), "A('z')", {"a": "z"}, "Str - no settings"),
        (field(), field(), "A(True)", {"a": True}, "Bool - no settings"),
        (field(), field(), "A([1, 2, 3])", {"a": [1, 2, 3]}, "List - no settings"),
        (primitized(), field(), "A(1)", {"a": 1}, "Int - no settings"),
        (primitized(), field(), "A('z')", {"a": "z"}, "Str - no settings"),
        (primitized(), field(), "A(True)", {"a": True}, "Bool - no settings"),
        (primitized(), field(), "A([1, 2, 3])", {"a": [1, 2, 3]}, "List - no settings"),
        (primitized(), field(), "A(B(1))", {"a": {"b": 1}}, "Nested - no settings"),
        (primitized(rename="z"), field(), "A(a=1)", {"z": 1}, "Rename"),
        (
            primitized(modifier=lambda o, v: v * 10),
            field(),
            "A(1)",
            {"a": 10},
            "Modifier",
        ),
        (
            field(),
            primitized(unset_if_empty=True),
            "A(B([]))",
            {"a": {}},
            "Unset if empty",
        ),
        (
            primitized(init=False),
            field(),
            "A()",
            {"a": None},
            "We need to support init=False",
        ),
    ],
)
def test_behavior(field_a, field_b, instanciation, expected, msg):
    @dataclass
    class A:
        a: Any = field_a

    @dataclass
    class B:
        b: Any = field_b

    obj = eval(instanciation)
    result = primitize(obj)
    assert result == expected, msg


@pytest.mark.parametrize(
    ("prim", "field"),
    [
        (
            primitized(modifier=1, validator=2),
            field(
                metadata={
                    "primitize": {
                        "rename": None,
                        "unset_if_empty": False,
                        "modifier": 1,
                        "validator": 2,
                    }
                }
            ),
        ),
        (
            primitized(rename="a", unset_if_empty=True, modifier=1, validator=2),
            field(
                metadata={
                    "primitize": {
                        "rename": "a",
                        "unset_if_empty": True,
                        "modifier": 1,
                        "validator": 2,
                    }
                }
            ),
        ),
        (
            primitized(modifier=1, validator=2, default=int),
            field(
                default=int,
                metadata={
                    "primitize": {
                        "rename": None,
                        "unset_if_empty": False,
                        "modifier": 1,
                        "validator": 2,
                    }
                },
            ),
        ),
        (
            primitized(modifier=1, validator=2, metadata={"foo": "bar"}),
            field(
                metadata={
                    "foo": "bar",
                    "primitize": {
                        "rename": None,
                        "unset_if_empty": False,
                        "modifier": 1,
                        "validator": 2,
                    },
                }
            ),
        ),
    ],
)
def test_primitized(prim, field):
    left = {f: getattr(field, f) for f in field.__slots__}
    right = {f: getattr(prim, f) for f in prim.__slots__}
    assert left == right


def test_no_deepcopy():
    @dataclass
    class _Obj:
        a: str

        def __reduce__(self):
            return tuple()  # Just break pickle

    o = _Obj(1)
    with pytest.raises(TypeError):
        deepcopy(o)  # Ensure the test is valid

    assert primitize(o) == {"a": 1}


def test_custom_primitize():
    prim = Mock()

    @dataclass
    class _Obj:
        a: str

        def primitize(self):
            return prim(self)

    o = _Obj(1)
    o.primitize()

    assert prim.call_args_list == [call(o)]
