from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from tz_canary.infer import _check_transition_occurs, infer_time_zone
from tz_canary.transitions_data import Transition


def test_infer_timezone():
    idx = pd.date_range(
        start="2023-01-01", end="2024-01-01", freq="15min", tz="Europe/Amsterdam"
    )
    assert infer_time_zone(idx) == {ZoneInfo("Europe/Amsterdam")}


def test_check_transition_occurs():
    idx = pd.date_range(
        start="2023-03-26", end="2023-03-27", freq="15min", tz="Europe/Amsterdam"
    )
    transition = Transition(
        utc_transition_time=datetime(2023, 3, 26, 1, tzinfo=ZoneInfo("UTC")),
        utc_offset=timedelta(seconds=7200),
        dst_offset=timedelta(seconds=3600),
        tz_name="CEST",
    )
    assert _check_transition_occurs(idx, "Europe/Amsterdam", transition)
