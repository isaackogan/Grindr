import json
import os
import asyncio
import pytest

from Grindr.web.routes.set.set_mobile_logs.event_schemas import MobileLogEvent, WebSocketEventLogData, ScreenshotObsNoPermLogData, AssignmentLoadSuccessLogData
from Grindr.web.routes.set.set_mobile_logs.set_mobile_logs import LogEventFlowPriority
from Grindr.web.web_client import GrindrWebClient
from examples.density import get_density
from Grindr.client.client import GrindrClient


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


@pytest.mark.asyncio
async def test_grindr_client_initialization():
    client = GrindrClient()
    email = os.environ.get('G_EMAIL')
    password = os.environ.get('G_PASSWORD')

    if not email or not password:
        pytest.skip("Environment variables G_EMAIL and G_PASSWORD must be set for this test.")

    await client.login(email=email, password=password)
    assert client._web.auth_session.credentials.email == email
    assert client._web.auth_session.credentials.password == password


@pytest.mark.asyncio
async def test_get_density():
    lat = 40.7128
    lon = -74.0060
    kms = 30

    email = os.environ.get('G_EMAIL')
    password = os.environ.get('G_PASSWORD')

    if not email or not password:
        pytest.skip("Environment variables G_EMAIL and G_PASSWORD must be set for this test.")

    client = GrindrClient()
    await client.login(email=email, password=password)

    density, measure_distance, measured_profiles = await get_density(lat, lon, kms=kms)
    assert isinstance(density, float)
    assert isinstance(measure_distance, float)
    assert isinstance(measured_profiles, int)


if __name__ == '__main__':
    test_log_flow()
    asyncio.run(test_grindr_client_initialization())
    asyncio.run(test_get_density())
