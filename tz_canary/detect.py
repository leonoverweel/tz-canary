from zoneinfo import ZoneInfo
import zoneinfo
from pprint import pprint
from datetime import datetime, timedelta
import pandas as pd

import pytz

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

from importlib import resources

# # America/New_York
# with resources.open_binary("tzdata.zoneinfo.Europe", "Amsterdam") as f:
#     print(f.read())


zone = pytz.timezone("Europe/Amsterdam")

transition_times = zone._utc_transition_times

print()
