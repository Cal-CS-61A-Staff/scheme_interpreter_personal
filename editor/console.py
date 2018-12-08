from typing import List

import gui
from datamodel import Expression, Undefined, String
from environment import global_attr
from evaluate_apply import Frame
from helper import verify_exact_callable_length
from primitives import SingleOperandPrimitive, BuiltIn


@global_attr("print")
class Print(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        gui.logger.out(operand)
        return Undefined


@global_attr("display")
class Display(SingleOperandPrimitive):
    def execute_simple(self, operand: Expression) -> Expression:
        if isinstance(operand, String):
            gui.logger.raw_out(operand.value)
        else:
            gui.logger.out(operand, end="")
        return Undefined


@global_attr("newline")
class Newline(BuiltIn):
    def execute_evaluated(self, operands: List[Expression], frame: Frame) -> Expression:
        verify_exact_callable_length(self, 0, len(operands))
        gui.logger.raw_out("\n")
        return Undefined
