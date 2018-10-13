from __future__ import annotations

from typing import Union


class Expression:
    def __repr__(self):
        return NotImplementedError()


class ValueHolder(Expression):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return str(self.value)


class Symbol(ValueHolder): pass


class Integer(ValueHolder): pass


class Pair(Expression):
    def __init__(self, first: Expression, rest: Union[Pair, Nil]):
        self.first = first
        self.rest = rest

    def __repr__(self):
        if isinstance(self.rest, Pair):
            return f"({self.first} {repr(self.rest)[1:-1]})"
        elif self.rest is Nil:
            return f"({self.first})"
        else:
            return f"({self.first} . {self.rest})"


class NilType(Expression):
    def __repr__(self):
        return "nil"


class Boolean(Expression):
    def __init__(self, val: bool):
        self.val = val
    def __repr__(self):
        if self.val:
            return "#t"
        else:
            return "#f"

SingletonTrue = Boolean(True)
SingletonFalse = Boolean(False)

Nil = NilType()