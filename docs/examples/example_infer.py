from pprint import pprint

import pandas as pd

from tz_canary import infer_time_zone

df = pd.read_csv("docs/data/example_data.csv", index_col="datetime", parse_dates=True)

plausible_time_zones = infer_time_zone(df.index)
pprint(plausible_time_zones)

# Output:
# {zoneinfo.ZoneInfo(key='Africa/Ceuta'),
#  zoneinfo.ZoneInfo(key='Arctic/Longyearbyen'),
#  zoneinfo.ZoneInfo(key='Europe/Amsterdam'),
#  ...
#  zoneinfo.ZoneInfo(key='Europe/Zurich')}
