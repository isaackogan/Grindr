import json

from Grindr.web.routes.set.set_mobile_logs.event_schemas import MobileLogEvent, WebSocketEventLogData, ScreenshotObsNoPermLogData, AssignmentLoadSuccessLogData
from Grindr.web.routes.set.set_mobile_logs.set_mobile_logs import LogEventFlowPriority
from Grindr.web.web_client import GrindrWebClient


def test_logs():
    """
    Test that all example logs can be parsed with the existing models. Current log list retrieved Jan 12.

    >>> test_logs()

    """

    data = json.load(open('example_logs.json', 'r'))

    for datum in data:
        MobileLogEvent(**datum)


def test_log_flow():
    client = GrindrWebClient()

    with client.set_mobile_logs.session(start_id=1) as session:
        ws_session_id = 1

        session += session.flow_from_data(
            WebSocketEventLogData(
                session_id=ws_session_id,
                event_id=0,
                event_type="Connecting"
            ),
            WebSocketEventLogData(
                session_id=ws_session_id,
                event_id=1,
                event_type="Connected",
            ),
            WebSocketEventLogData(
                session_id=ws_session_id,
                event_id=2,
                event_type="Closed",
                code=1000,
                message="Normal closure"
            ),
            shuffle=False,
            priority=LogEventFlowPriority.HIGHEST
        )

        session += session.event_from_data(
            data=ScreenshotObsNoPermLogData()
        )

        session += session.event_from_data(
            data=AssignmentLoadSuccessLogData()
        )

        print(list(session.unpack()))


if __name__ == '__main__':
    test_log_flow()
