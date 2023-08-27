import pandas as pd

from tz_canary import validate_time_zone

df = pd.read_csv("docs/data/example_data.csv", index_col="datetime", parse_dates=True)

validate_time_zone(df.index, "Europe/Amsterdam")  # will pass
validate_time_zone(df.index, "America/New_York")  # will raise ImplausibleTimeZoneError
validate_time_zone(df.index, "UTC")  # will raise ImplausibleTimeZoneError
