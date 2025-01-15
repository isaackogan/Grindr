from __future__ import annotations

import enum
import time
from typing import Generator

from Grindr.client.web.web_base import ClientRoute, URLTemplate, BodyParams
from Grindr.client.web.web_settings import GRINDR_V3
from .event_schemas import *

type EventFlowSequence = list[MobileLogEvent | LogEventFlow]


class LogEventFlowPriority(int, enum.Enum):
    """Relative priority of an event"""

    LOWEST = 1
    LOW = 2
    NORMAL = 3
    HIGH = 4
    HIGHEST = 5


class LogEventFlow(BaseModel):
    """Events in LogEventFlow batches will be sent together"""

    sequence: EventFlowSequence
    shuffle: bool = True
    priority: LogEventFlowPriority = LogEventFlowPriority.LOWEST  # Events have a priority of LOWEST when not specified

    def unpack(self) -> Generator[MobileLogEvent]:
        """
        Unpack the flow into a sequence of events.
        :return: The unpacked events, with priority & shuffling applied

        """

        # Bin the flow events by priority. "Raw" events are given the lowest priority.
        event_bins: list[list[EventFlowSequence]] = [list() for _ in range(LogEventFlowPriority.HIGHEST.value)]

        # First we bin the events by priority
        for item in self.sequence:

            # Events outside a flow are treated as lowest priority
            if isinstance(item, MobileLogEvent):
                event_bins[-LogEventFlowPriority.NORMAL.value].append(item)

            # Flows must be added to the correct priority bin
            elif isinstance(item, LogEventFlow):
                event_bins[-item.priority.value].append(item)

            else:
                raise TypeError(f"Cannot unpack {type(item)}")

        # Within each priority we can handle shuffling & unpacking
        for event_bin in event_bins:

            # Shuffle items within the bin
            if self.shuffle:
                random.shuffle(event_bin)

            # Unpack each item in the bin
            for item in event_bin:
                if isinstance(item, MobileLogEvent):
                    yield item

                elif isinstance(item, LogEventFlow):
                    yield from item.unpack()


class SetMobileLogsRoutePayload(BodyParams):
    events: list[MobileLogEvent]

    @classmethod
    def from_flow(cls, flow: LogEventFlow) -> SetMobileLogsRoutePayload:
        """Build from a flow item directly"""

        return cls(
            events=list(flow.unpack())
        )


class MobileLogEventSession:
    """A session of mobile log events"""

    def __init__(
            self,
            *,
            start_log_id: int,
            start_time: int,
            route: SetMobileLogsRoute,
            shuffle: bool = False,
    ):
        """
        A session of mobile log events

        :param start_log_id: The starting ID for the events

        """

        self._route = route
        self._current_log_id = start_log_id - 1
        self._flow = LogEventFlow(sequence=[], shuffle=shuffle)
        self._current_time: int = start_time

        self._log_session_id: str = ""
        self._cascade_session_id: str = ""

        self._ws_session_id: int = 0
        self._ws_event_id: int = 0
        self._current_page: str = "HomeActivity"

    def set_log_session_id(self, session_id: str) -> None:
        self._log_session_id = session_id

    def set_cascade_session_id(self, session_id: str) -> None:
        self._cascade_session_id = session_id

    def set_current_page(self, page: str) -> str:
        self._current_page = page
        return self._current_page

    @property
    def current_page(self) -> str:
        return self._current_page

    @property
    def cascade_session_id(self) -> str:
        return self._cascade_session_id

    @property
    def log_session_id(self) -> str:
        return self._log_session_id

    def set_websocket_session_id(self, session_id: int) -> None:
        self._ws_session_id = session_id

    @property
    def websocket_session_id(self) -> int:
        self._ws_event_id = 0
        return self._ws_session_id

    @property
    def web(self):
        return self._route.web

    def __add__(self, other: EventFlowSequence) -> MobileLogEventSession:

        if not isinstance(other, list):
            raise TypeError(f"Cannot add {type(other)} to MobileLogEventSession")

        for item in other:
            if isinstance(item, MobileLogEvent) or isinstance(item, LogEventFlow):
                self._flow.sequence.append(item)
            if isinstance(item, list):
                self._flow.sequence.extend(item)

        return self

    async def send(self) -> None:
        """Send the events in this session"""

        return await self._route(
            body=SetMobileLogsRoutePayload.from_flow(
                flow=self._flow
            )
        )

    @property
    def flow(self) -> LogEventFlow:
        return self._flow

    def unpack(self) -> Generator[MobileLogEvent]:
        return self._flow.unpack()

    def __enter__(self):
        return self

    def clear(self):
        self._flow.sequence.clear()

    def event_from_data(
            self,
            data: BaseLogEventData
    ) -> MobileLogEvent:
        self._current_log_id += 1

        if isinstance(data, WebSocketEventLogData):
            data.event_id = self._ws_event_id
            data.session_id = self._ws_session_id
            self._ws_event_id += 1

        return MobileLogEvent(
            id=self._current_log_id,
            params=data,
            name=data.event_name,
            timestamp=int(time.time() * 1000)
        )

    def flow_from_data(
            self,
            *data: BaseLogEventData,
            shuffle: bool = True,
            priority: LogEventFlowPriority = LogEventFlowPriority.LOWEST,
            flow_duration: int
    ) -> LogEventFlow:
        """Create a flow in this session"""
        events = len(data)
        time_per_event = flow_duration / events

        for item in data:
            event = self.event_from_data(data=item)
            event.timestamp = self._current_time + time_per_event
            self._current_time += time_per_event

        return LogEventFlow(
            sequence=[self.event_from_data(data=item) for item in data],
            shuffle=shuffle,
            priority=priority
        )

    @property
    def current_log_id(self) -> int:
        return self._current_log_id

    @property
    def current_time(self) -> int:
        return self._current_time


class SetMobileLogsRoute(
    ClientRoute[
        "POST",
        URLTemplate(GRINDR_V3, "/logging/mobile/logs"),
        None,
        SetMobileLogsRoutePayload,
        None
    ]
):

    def session(
            self,
            start_id: int,
            shuffle: bool = True,
            start_time: int = int(time.time() * 1000)
    ) -> MobileLogEventSession:
        """Create a session for mobile log events. The ID seems to be an incrementing number that is persistent BETWEEN sessions. Hence no default parameter."""

        return MobileLogEventSession(
            start_log_id=start_id,
            route=self,
            shuffle=shuffle,
            start_time=start_time
        )
