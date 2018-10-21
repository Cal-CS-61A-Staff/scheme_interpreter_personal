from datamodel import Symbol, Nil, SingletonTrue, SingletonFalse
from evaluate_apply import Frame


def make_frame_decorator(defdict):
    def global_builtin(name):
        def decorator(cls):
            cls.__repr__ = lambda self: f"#[{name}]"
            defdict[Symbol(name)] = cls()
            return cls

        return decorator

    return global_builtin


defdict = {}
global_attr = make_frame_decorator(defdict)


def build_global_frame():
    frame = Frame("builtins")
    for k, v in defdict.items():
        frame.assign(k, v)
    frame.assign(Symbol("nil"), Nil)
    frame.assign(Symbol("#t"), SingletonTrue)
    frame.assign(Symbol("#f"), SingletonFalse)
    return Frame("Global", frame)
