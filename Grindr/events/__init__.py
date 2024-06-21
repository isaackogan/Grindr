from typing import Union, TypeVar, Callable, Awaitable

from .events import *

EventHandler = TypeVar("EventHandler", bound=Callable[[Event], Union[None, Awaitable[None]]])
