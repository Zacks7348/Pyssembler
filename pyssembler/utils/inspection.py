import inspect
from typing import *

__all__ = ['is_inside_class', 'extract_arguments_from_func']


def is_inside_class(func: Callable[..., Any]) -> bool:
    # For methods defined in a class, the qualname has a dotted path
    # denoting which class it belongs to. So, e.g. for A.foo the qualname
    # would be A.foo while a global foo() would just be foo.
    #
    # Unfortunately, for nested functions this breaks. So inside an outer
    # function named outer, those two would end up having a qualname with
    # outer.<locals>.A.foo and outer.<locals>.foo

    if func.__qualname__ == func.__name__:
        return False

    (remaining, _, _) = func.__qualname__.rpartition('.')
    return not remaining.endswith('<locals>')


def extract_arguments_from_func(func: Callable[..., Any]) -> Generator[inspect.Parameter, None, None]:
    """Extracts arguments from a function"""
    params = inspect.signature(func).parameters
    required_params = int(is_inside_class(func))

    for i, parameter in enumerate(params.values()):
        if i >= required_params:
            yield parameter
