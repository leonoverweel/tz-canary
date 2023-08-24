from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd
import pytest

from tz_canary.infer import _check_transition_occurs, infer_time_zone
from tz_canary.transitions_data import Transition


@pytest.fixture
def idx_ams_2023():
    return pd.date_range(
        start="2023-01-01", end="2023-12-31 23:45:00", freq="15T", tz="Europe/Amsterdam"
    ).tz_localize(None)


@pytest.fixture
def idx_ny_2023():
    return pd.date_range(
        start="2023-01-01", end="2023-12-31 23:45:00", freq="15T", tz="America/New_York"
    ).tz_localize(None)


@pytest.fixture
def tr_ams_2023_spring():
    return Transition(
        utc_transition_time=datetime(2023, 3, 26, 1, tzinfo=ZoneInfo("UTC")),
        utc_offset=timedelta(seconds=7200),
        dst_offset=timedelta(seconds=3600),
        tz_name="CEST",
    )


@pytest.mark.parametrize(
    "dt_index, expected, not_expected",
    [
        ("idx_ams_2023", "Europe/Amsterdam", {"UTC", "America/New_York"}),
        ("idx_ny_2023", "America/New_York", {"UTC", "Europe/Amsterdam"}),
    ],
)
def test_infer_timezone(dt_index, expected, not_expected, request):
    result = infer_time_zone(request.getfixturevalue(dt_index))

    # Check that the expected time zone is in the result
    assert {ZoneInfo(expected)}.issubset(result)

    # Check that the not expected time zones are not in the result
    assert not {ZoneInfo(tz) for tz in not_expected}.issubset(result)


@pytest.mark.parametrize(
    "dt_index, transition, candidate_tz_name, expected",
    [
        ("idx_ams_2023", "tr_ams_2023_spring", "Europe/Amsterdam", True),
        ("idx_ny_2023", "tr_ams_2023_spring", "America/New_York", False),
    ],
)
def test_check_transition_occurs(
    dt_index, transition, candidate_tz_name, expected, request
):
    result = _check_transition_occurs(
        request.getfixturevalue(dt_index),
        candidate_tz_name,
        request.getfixturevalue(transition),
    )
    assert result == expected
