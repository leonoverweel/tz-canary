from zoneinfo import ZoneInfo

import pytest

from tz_canary.infer import _check_transition_occurs, infer_time_zone


@pytest.mark.parametrize(
    "dt_index, expected, not_expected",
    [
        ("idx_ams_2023", "Europe/Amsterdam", {"UTC", "America/New_York"}),
        ("idx_ny_2023", "America/New_York", {"UTC", "Europe/Amsterdam"}),
        # ("idx_utc_2023", "UTC", {"Europe/Amsterdam", "America/New_York"}),
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
        ("idx_ams_2022", "tr_ams_2023_spring", "Europe/Amsterdam", None),
        ("idx_ams_2023", "tr_ams_2023_spring", "Europe/Amsterdam", True),
        ("idx_ny_2023", "tr_ams_2023_spring", "America/New_York", False),
        ("idx_ams_2023", "tr_ams_2023_fall", "Europe/Amsterdam", True),
        ("idx_ny_2023", "tr_ams_2023_fall", "America/New_York", False),
        ("idx_utc_2023", "tr_ams_2023_spring", "UTC", False),
        ("idx_utc_2023", "tr_ams_2023_fall", "UTC", False),
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
