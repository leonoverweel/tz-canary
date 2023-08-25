from zoneinfo import ZoneInfo

import pytest

from tz_canary.exceptions import ImplausibleTimeZoneError
from tz_canary.validate import validate_time_zone


@pytest.mark.parametrize(
    "dt_index, time_zone, should_raise",
    [
        ("idx_ams_2023", "Europe/Amsterdam", False),
        ("idx_ams_2023", "America/New_York", True),
        ("idx_ams_2023", "UTC", True),
        ("idx_ny_2023", "Europe/Amsterdam", True),
        ("idx_ny_2023", "America/New_York", False),
        ("idx_ny_2023", "UTC", True),
    ],
)
def test_validate_time_zone(dt_index, time_zone, should_raise, request):
    dt_index = request.getfixturevalue(dt_index)
    time_zone = ZoneInfo(time_zone)

    if not should_raise:
        validate_time_zone(dt_index, time_zone)

    else:
        with pytest.raises(ImplausibleTimeZoneError):
            validate_time_zone(dt_index, time_zone)
