from dataclasses import dataclass

from primitize.core import primitize
from typing import List


def test_simple():
    @dataclass
    class Test:
        a: int
        b: str
        c: bool
        d: List[int]

    o = Test(1, "z", True, [1, 2, 3])
    r = primitize(o)
    assert r == {"a": 1, "b": "z", "c": True, "d": [1, 2, 3]}
