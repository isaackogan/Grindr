import doctest
import json

from Grindr.client.web.routes.set.set_mobile_logs.event_schemas import MobileLogEvent


def test_logs():
    """
    Test that all example logs can be parsed with the existing models. Current log list retrieved Jan 12.

    >>> test_logs()

    """

    data = json.load(open('example_logs.json', 'r'))

    for datum in data:
        MobileLogEvent(**datum)


doctest.testmod()
