"""
A custom event handling system.

Here are the events that are triggered by the Pyssembler simulator:
    onInstructionFetch(pc: int, instruction: ProgramLine)
    onInstructionExecute(pc: int, instruction: ProgramLine)
    onMemoryWrite(address: int, value: int, size: int)
    onRegisterWrite(address: int, processor: ['GPR', 'CP0', 'CP1'], value: int)
    onSimulationStart(pc_start: int)
    onSimulationStop(pc_end: int, exit_code: int)
    onSimulationException(pc: int, exception_code: int)
"""

from typing import Callable, Dict, List

# Stores a list of handlers for each event
__events: Dict[str, List[Callable]] = {
    'onMemoryWrite': []
}


def listener(event: str) -> Callable:
    """
    Registers a handler to an event.

    Used as a decorator with the signature @listener(event)
    """
    def wrapper(handler: Callable) -> None:
        if event in __events:
            __events[event].append(handler)
            return
        __events[event] = [handler]
    return wrapper

def trigger(event: str, *args, **kwargs):
    """
    Triggers an event.

    Handlers are called in the order that they were registered.
    """
    for handler in __events.get(event, []):
        handler(*args, **kwargs)


def add_listener(event: str, handler: Callable) -> None:
    """
    Adds a handler to event. 

    Functional equivalent to the listener decorator.
    """
    if event in __events:
        __events[event].append(handler)
        return
    __events[event] = [handler]


def remove_listener(event: str, handler: Callable) -> None:
    """
    Removes the handler from event
    """
    __events[event].remove(handler)


def get_listeners(event: str) -> List[Callable]:
    """
    Returns a shallow copy of the list of handlers for event
    """
    if not event in __events:
        return []
    return __events[event].copy()
