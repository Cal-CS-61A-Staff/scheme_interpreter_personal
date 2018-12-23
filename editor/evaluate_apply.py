from __future__ import annotations

from abc import ABC
from typing import Dict, List, Union

from datamodel import Symbol, Expression, Number, Pair, Nil, Undefined, Boolean, String, Promise
import log
from scheme_exceptions import SymbolLookupError, CallableResolutionError, IrreversibleOperationError
from helper import pair_to_list


class Frame:
    def __init__(self, name: str, parent: Frame = None):
        self.parent = parent
        self.name = name
        self.vars: Dict[str, Expression] = {}
        self.id = "unknown - an error has occurred"
        self.temp = log.logger.fragile
        log.logger.frame_create(self)

    def assign(self, varname: Symbol, varval: Expression):
        if log.logger.fragile and not self.temp:
            raise IrreversibleOperationError()
        self.vars[varname.value] = varval
        log.logger.frame_store(self, varname.value, varval)

    def lookup(self, varname: Symbol):
        if varname.value in self.vars:
            return self.vars[varname.value]
        if self.parent is None:
            raise SymbolLookupError(f"Variable not found in current environment: '{varname}'")
        return self.parent.lookup(varname)

    def __hash__(self):
        return id(self)

    def __repr__(self):
        return repr(self.vars)


class Thunk:
    def __init__(self, expr: Expression, frame: Frame, log_stack: bool = True):
        self.expr = expr
        self.frame = frame
        self.log_stack = log_stack

    def __repr__(self):
        return "thunk"


def evaluate(expr: Expression, frame: Frame, gui_holder: log.Holder,
             tail_context: bool = False, *, log_stack: bool=True) -> Union[Expression, Thunk]:
    """
    >>> global_frame = __import__("special_forms").build_global_frame()
    >>> gui_holder = __import__("gui").Holder(None)
    >>> __import__("gui").Root.setroot(gui_holder)
    >>> __import__("gui").silent = True

    >>> buff = __import__("lexer").TokenBuffer(["(+ 1 2)"])
    >>> expr = __import__("parser").get_expression(buff)
    >>> result = evaluate(expr, global_frame, gui_holder)
    >>> print(result)
    3
    >>> evaluate(__import__("parser").get_expression(__import__("lexer").TokenBuffer(["(+ 3 4 5)"])), global_frame, gui_holder)
    12
    >>> evaluate(__import__("parser").get_expression(__import__("lexer").TokenBuffer(["(* 3 4 5)"])), global_frame, gui_holder)
    60
    >>> evaluate(__import__("parser").get_expression(__import__("lexer").TokenBuffer(["(* (+ 1 2) 4 5)"])), global_frame, gui_holder)
    60
    >>> __import__("gui").silent = False
    """

    depth = 0
    while True:
        if isinstance(gui_holder.expression, Expression):
            visual_expression = log.VisualExpression(expr)
            gui_holder.link_visual(visual_expression)
        else:
            visual_expression = gui_holder.expression

        if log_stack:
            log.logger.eval_stack.append(f"{repr(expr)} [frame = {frame.id}]")
            depth += 1

        if isinstance(expr, Number) \
                or isinstance(expr, Callable) \
                or isinstance(expr, Boolean) \
                or isinstance(expr, String) \
                or isinstance(expr, Promise):
            gui_holder.complete()
            visual_expression.value = expr
            ret = expr
        elif isinstance(expr, Symbol):
            gui_holder.evaluate()
            out = frame.lookup(expr)
            from special_forms import MacroObject
            if isinstance(out, Callable) and not isinstance(out, Applicable) and not isinstance(out, MacroObject):
                raise SymbolLookupError(f"Variable not found in current environment: '{expr.value}'")
            visual_expression.value = out
            gui_holder.complete()
            ret = out
        elif isinstance(expr, Pair):
            if tail_context and False:
                ret = Thunk(expr, frame, log_stack)
            else:
                gui_holder.evaluate()
                operator = expr.first
                if isinstance(operator, Symbol) \
                        and isinstance(frame.lookup(operator), Callable) \
                        and not isinstance(frame.lookup(operator), Applicable):
                    operator = frame.lookup(operator)
                else:
                    operator = evaluate(operator, frame, visual_expression.children[
                        0])  # evaluating operator and storing it in visual_expression
                operands = pair_to_list(expr.rest)
                out = apply(operator, operands, frame, gui_holder)
                if isinstance(out, Thunk):
                    expr, frame = out.expr, out.frame
                    gui_holder.expression.update(expr)
                    continue
                visual_expression.value = out
                gui_holder.complete()
                ret = out
        elif expr is Nil or expr is Undefined:
            visual_expression.value = expr
            gui_holder.complete()
            ret = expr
        else:
            raise Exception("Internal error. Please report to maintainer!")

        for _ in range(depth):
            log.logger.eval_stack.pop()

        return ret


def apply(operator: Expression, operands: List[Expression], frame: Frame, gui_holder: log.Holder):
    if isinstance(operator, Callable):
        return operator.execute(operands, frame, gui_holder)
    elif isinstance(operator, Symbol):
        raise CallableResolutionError(f"Unable to pass parameters into the Symbol '{operator}'")
    else:
        raise CallableResolutionError(f"Unable to pass parameters into: '{operator}'")


class Callable(Expression):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: log.Holder):
        raise NotImplementedError()


class Applicable(Callable):
    def execute(self, operands: List[Expression], frame: Frame, gui_holder: log.Holder, eval_operands=True):
        raise NotImplementedError()


def evaluate_all(operands: List[Expression], frame: Frame, operand_holders: List[log.Holder]) -> List[Expression]:
    return [evaluate(operand, frame, holder) for operand, holder in zip(operands, operand_holders)]
