from typing import Type, Optional, Callable, Union

from pyee.asyncio import AsyncIOEventEmitter
from pyee.base import Handler

from Grindr.events import Event


class GrindrEmitter(AsyncIOEventEmitter):

    def on(self, event: Type[Event], f: Optional[Callable] = None) -> Union[Handler, Callable[[Handler], Handler]]:
        """
        Decorator that can be used to register a Python function as an event listener

        :param event: The event to listen to
        :param f: The function to handle the event
        :return: The wrapped function as a generated `pyee.Handler` object

        """

        return super(GrindrEmitter, self).on(event.get_event_type(), f)

    def add_listener(self, event: Type[Event], f: Callable) -> Handler:
        """
        Method that can be used to register a Python function as an event listener

        :param event: The event to listen to
        :param f: The function to handle the event
        :return: The generated `pyee.Handler` object

        """
        if isinstance(event, str):
            return super().add_listener(event=event, f=f)

        return super().add_listener(event=event.get_event_type(), f=f)

    def has_listener(self, event: Type[Event]) -> bool:
        """
        Check whether the client is listening to a given event

        :param event: The event to check listening for
        :return: Whether it is being listened to

        """

        return event.__name__ in self._events

    def remove_listener(self, event: Type[Event], f: Callable) -> None:
        """
        Remove a listener from the event emitter

        :param event: The event to remove the listener from
        :param f: The listener to remove

        """

        if isinstance(event, str):
            return super().remove_listener(event=event, f=f)

        return super().remove_listener(event=event.get_event_type(), f=f)

    def remove_all_listeners(self, event: Type[Event] = None) -> None:
        """
        Remove all listeners from the event emitter

        :param event: The event to remove all listeners from

        """

        if event is None:
            return super().remove_all_listeners()

        return super().remove_all_listeners(event.get_event_type())
