import zoneinfo
from datetime import datetime, timedelta
from importlib import resources
from pprint import pprint
from typing import Set
from zoneinfo import ZoneInfo

import pandas as pd
import pytz

from tz_canary.transitions_data import TransitionsData

# dt = datetime(2023, 3, 26, 2, 30, tzinfo=ZoneInfo("Europe/Amsterdam"))
# print(dt)
# print(dt.tzname())

# pprint(zoneinfo.available_timezones())

# rng = pd.date_range(start="2023-03-26 02:00", end="2023-03-26 03:00", freq="15min", tz="Europe/Amsterdam")
# print(rng)

# dt2 = pd.Timestamp("2023-03-26 02:00", tz="Europe/Amsterdam")
# dt3 = pd.Timestamp(2023, 3, 26, 2, 0, 0, tz="Europe/Amsterdam")
# print(dt3)
#
# zone = ZoneInfo("Europe/Amsterdam")
# print(zone.utcoffset(datetime(2023, 1, 1)))


# # America/New_York
# with resources.open_binary("tzdata.zoneinfo.Europe", "Amsterdam") as f:
#     print(f.read())


def infer_time_zone(
    dt_index: pd.DatetimeIndex, transition_data: TransitionsData = None
) -> Set[ZoneInfo]:
    if transition_data is None:
        transition_data = TransitionsData(
            year_start=dt_index.min().year, year_end=dt_index.max().year
        )

    # Remove time zone if set
    reported_tz = dt_index.tz
    dt_index = dt_index.tz_localize(None)

    # Find plausible time zones
    plausible_tz = set()
    for tz_name, transitions in transition_data.tz_transitions.items():
        if tz_name != "Europe/Amsterdam" and tz_name != "America/New_York":
            continue  # TODO - remove this
        if any(_check_transition_occurs(dt_index, t) for t in transitions):
            plausible_tz.add(ZoneInfo(tz_name))

    return plausible_tz


def _check_transition_occurs(dt_index: pd.DatetimeIndex, transition: dict) -> bool:
    dt_index = dt_index.tz_localize(None)  # To enable comparison with transition time
    if (
        transition["utc_transition_time"] < dt_index.min()
        or transition["utc_transition_time"] > dt_index.max()
    ):
        return False

    # TODO - check if transition occurs in dt_index

    return True
