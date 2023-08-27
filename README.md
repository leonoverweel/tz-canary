# `tz-canary` - Time Zone Canary

In a perfect world, all time series data is time-zone-aware and stored in UTC.
Sadly, we do not live in a perfect world.
Time series data often lacks a time zone identifier, or worse, does not actually adhere to the time zone it claims to be in.

`tz-canary` inspects the Daylight Savings Time (DST) switches in a time series to infer a set of plausible time zones the data could be in.
It allows you to **infer** the full set of plausible time zones for the data, or to **validate** whether a given time zone is plausible for the data.

## Installation

TODO - after pushing v0.1.0 to PyPI

## Usage

The simplest way to use `tz-canary` is to validate a given time zone for a time series:

```python
import pandas as pd
from tz_canary import validate_time_zone

df = pd.read_csv("docs/data/example_data.csv", index_col="datetime", parse_dates=True)

validate_time_zone(df.index, "Europe/Amsterdam")  # will pass
validate_time_zone(df.index, "America/New_York")  # will raise ImplausibleTimeZoneError
validate_time_zone(df.index, "UTC")  # will raise ImplausibleTimeZoneError
```

You can also get a list of all plausible time zones for a time series:

```python
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
```

TODO - add example for building a `TransitionsData` object and using that to validate/infer many time series.

## Development

TODO - add overview of setup (git LFS, poetry, pre-commit, pytest, etc.)

## Contributing

TODO - add contributing guidelines
