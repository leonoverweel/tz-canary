from typing import Optional, Union
from zoneinfo import ZoneInfo

import pandas as pd

from tz_canary.exceptions import ImplausibleTimeZoneError
from tz_canary.infer import infer_time_zone
from tz_canary.transitions_data import TransitionsData


def validate_time_zone(
    dt_index: pd.DatetimeIndex,
    time_zone: Union[str, ZoneInfo] = None,
    transition_data: Optional[TransitionsData] = None,
) -> None:
    """Validate that the given time zone is plausible given DST changes in the index.

    This function can be used in one of two ways:
    1. If `dt_index` has a time zone, this function will check whether it is plausible.
    2. If `dt_index` has no time zone but the `time_zone` argument is given, this
         function will check whether that time zone is plausible.

    You cannot pass both a `time_zone` and a time-zone-aware `dt_index`.

    Args:
        dt_index: A pandas DatetimeIndex. If `dt_index` is time-zone-aware, its time
            zone will be validated. If `dt_index` time-zone-naive, the `time_zone`
            argument must be given.
        time_zone: A time zone to validate. If `time_zone` is given, `dt_index` must be
            time-zone-naive.
        transition_data: A TransitionsData object. If None, the TransitionsData will be
            built for the years spanning the given index. When inferring time zones for
            many indices, it is more efficient to build a TransitionsData object once
            and pass it to multiple calls of this function.

    Raises:
        ImplausibleTimeZoneError: If the given time zone is implausible.
        ValueError: If both `dt_index` and `time_zone` are given.
    """

    if (dt_index.tz is None) == (time_zone is None):
        raise ValueError(
            "Pass either a time-zone-aware `dt_index` or a `time_zone`, but not both. "
            "If `dt_index` is time-zone-naive, pass a `time_zone`. "
            "If `dt_index` is time-zone-aware, do not pass a `time_zone`."
        )

    given_time_zone = time_zone or dt_index.tz  # TODO - normalize to ZoneInfo
    if isinstance(given_time_zone, str):
        given_time_zone = ZoneInfo(given_time_zone)

    plausible_time_zones = infer_time_zone(dt_index, transition_data)

    if given_time_zone not in plausible_time_zones:
        raise ImplausibleTimeZoneError(
            f"The given time zone `{given_time_zone}` is not plausible for `dt_index`. "
            f"It may be one of: `{sorted([tz.key for tz in plausible_time_zones])}`."
        )
