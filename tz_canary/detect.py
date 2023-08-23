from zoneinfo import ZoneInfo
import zoneinfo
from pprint import pprint
from datetime import datetime, timedelta
import pandas as pd

# dt = datetime(2023, 3, 26, 2, 30, tzinfo=ZoneInfo("Europe/Amsterdam"))
# print(dt)
# print(dt.tzname())

# pprint(zoneinfo.available_timezones())

# rng = pd.date_range(start="2023-03-26 02:00", end="2023-03-26 03:00", freq="15min", tz="Europe/Amsterdam")
# print(rng)

# dt2 = pd.Timestamp("2023-03-26 02:00", tz="Europe/Amsterdam")
# dt3 = pd.Timestamp(2023, 3, 26, 2, 0, 0, tz="Europe/Amsterdam")
# print(dt3)

print(pd.show_versions())