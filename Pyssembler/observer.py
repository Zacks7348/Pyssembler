from typing import Callable


class Observable:
    """
    Interface for observable classes.

    To see how to notify observers see notify_observers
    """
    def __init__(self):
        self.__observers = []

    def add_observer(self, observer: Callable):
        self.__observers.append(observer)

    def remove_observer(self, observer: Callable):
        self.__observers.remove(observer)

    def notify_observers(self):
        """
        Generic function to notify observers with no arguments.
        """
        for observer in self.observers:
            observer()

    @property
    def observers(self):
        return iter(self.__observers)

