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
                event_bins[-LogEventFlowPriority.LOWEST.value].append(item)

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
            start_id: int,
            route: SetMobileLogsRoute,
            shuffle: bool = False,
    ):
        """
        A session of mobile log events

        :param start_id: The starting ID for the events

        """

        self._route = route
        self._original_id = start_id - 1
        self._id = self._original_id + 0
        self._flow = LogEventFlow(sequence=[], shuffle=shuffle)

    def __add__(self, other: EventFlowSequence | MobileLogEvent) -> MobileLogEventSession:
        # Add the other item to the flow
        if isinstance(other, LogEventFlow) or isinstance(other, MobileLogEvent):
            self._flow.sequence.append(other)
            return self

        raise TypeError(f"Cannot add {type(other)} to MobileLogEventSession")

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

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear()

    def clear(self):
        self._flow.sequence.clear()
        self._id = self._original_id

    def event_from_data(
            self,
            data: BaseLogEventData
    ) -> MobileLogEvent:
        self._id += 1
        return MobileLogEvent(
            id=self._id,
            params=data,
            name=data.event_name,
            timestamp=int(time.time() * 1000)
        )

    def flow_from_data(
            self,
            *data: BaseLogEventData,
            shuffle: bool = True,
            priority: LogEventFlowPriority = LogEventFlowPriority.LOWEST
    ) -> LogEventFlow:
        """Create a flow in this session"""

        return LogEventFlow(
            sequence=[self.event_from_data(data=item) for item in data],
            shuffle=shuffle,
            priority=priority
        )


class SetMobileLogsRoute(
    ClientRoute[
        "GET",
        URLTemplate(GRINDR_V3, "/logging/mobile/logs"),
        None,
        SetMobileLogsRoutePayload,
        None
    ]
):

    def session(
            self,
            start_id: int,
            shuffle: bool = True
    ) -> MobileLogEventSession:
        """Create a session for mobile log events. The ID seems to be an incrementing number that is persistent BETWEEN sessions. Hence no default parameter."""

        return MobileLogEventSession(
            start_id=start_id,
            route=self,
            shuffle=shuffle
        )
