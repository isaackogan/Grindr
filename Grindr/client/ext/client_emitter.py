from typing import Callable, Any, Type

from pydantic import BaseModel
from pyee.asyncio import AsyncIOEventEmitter

from Grindr.ws.events.events import BaseWebSocketEventPayload

type Handler[T: BaseWebSocketEventPayload] = Callable[[T], Any]
type EventPayload = Type[BaseWebSocketEventPayload]


class GrindrEventEmitter(AsyncIOEventEmitter):

    def on[T: EventPayload](self, event: T, f: Handler[T] | None = None) -> Handler[T] | Callable[[Handler[T]], Handler[T]]:
        """
        Decorator that can be used to register a Python function as an event listener

        :param event: The event to listen to
        :param f: The function to handle the event
        :return: The wrapped function as a generated `pyee.Handler` object

        """

        return super(GrindrEventEmitter, self).on(event.event_name(), f)

    def add_listener(self, event: EventPayload, f: Handler) -> Handler:
        """
        Method that can be used to register a Python function as an event listener

        :param event: The event to listen to
        :param f: The function to handle the event
        :return: The generated `pyee.Handler` object

        """

        if isinstance(event, str):
            return super().add_listener(event=event, f=f)

        return super().add_listener(event=event.event_name(), f=f)

    def has_listener(self, event: EventPayload) -> bool:
        """
        Check whether the client is listening to a given event

        :param event: The event to check listening for
        :return: Whether it is being listened to

        """

        return event.__name__ in self._events

    def remove_listener(self, event: EventPayload, f: Handler) -> None:
        """
        Remove a listener from the event emitter

        :param event: The event to remove the listener from
        :param f: The listener to remove

        """

        if isinstance(event, str):
            return super().remove_listener(event=event, f=f)

        return super().remove_listener(event=event.event_name(), f=f)

    def remove_all_listeners(self, event: EventPayload = None) -> None:
        """
        Remove all listeners from the event emitter

        :param event: The event to remove all listeners from

        """

        if event is None:
            return super().remove_all_listeners()

        return super().remove_all_listeners(event.event_name())

    def emit(
            self,
            event: str | EventPayload,
            *args: Any,
            **kwargs: Any,
    ) -> bool:
        """
        Emit an event to all listeners

        :param event: The event to emit
        :param args: The arguments to pass to the listeners
        :param kwargs: The arguments to pass to the listeners
        :return: True if any listeners were called

        """

        if isinstance(event, BaseWebSocketEventPayload):
            return super().emit(event.event_name(), *[event, *args], **kwargs)

        return super().emit(event, *args, **kwargs)
