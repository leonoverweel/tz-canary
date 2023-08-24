import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from tz_canary.transitions_data import Transition


@pytest.fixture
def tr_ams_2023_spring():
    return Transition(
        utc_transition_time=datetime(2023, 3, 26, 1, tzinfo=ZoneInfo("UTC")),
        utc_offset=timedelta(seconds=7200),
        dst_offset=timedelta(seconds=3600),
        tz_name="CEST",
    )
