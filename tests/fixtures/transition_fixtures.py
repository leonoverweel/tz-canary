from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from tz_canary.transitions_data import Transition


@pytest.fixture
def tr_ams_2023_spring():
    return Transition(
        utc_transition_time=datetime(2023, 3, 26, 1, tzinfo=ZoneInfo("UTC")),
        utc_offset=timedelta(seconds=7200),
        dst_offset=timedelta(seconds=3600),
        tz_name="CEST",
    )


@pytest.fixture
def tr_ams_2023_fall():
    return Transition(
        utc_transition_time=datetime(2023, 10, 29, 1, tzinfo=ZoneInfo(key="UTC")),
        utc_offset=timedelta(seconds=3600),
        dst_offset=timedelta(0),
        tz_name="CET",
    )
