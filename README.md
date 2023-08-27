# `tz-canary` - Time Zone Canary

In a perfect world, all time series data is time-zone-aware and stored in UTC.
Sadly, we do not live in a perfect world.
Time series data often lacks a time zone identifier, or worse, does not actually adhere to the time zone it claims to be in.

`tz-canary` inspects the Daylight Savings Time (DST) switches in a time series to infer a set of plausible time zones the data could be in.
It allows you to **infer** the full set of plausible time zones for the data, or to **validate** whether a given time zone is plausible for the data.

## Installation

`tz-canary` is available on PyPI, so you can install it just like any other Python package:

```bash
pip install tz-canary
```

## Usage

### Time zone validation

The simplest way to use `tz-canary` is to validate a given time zone for a time series:

```python
import pandas as pd
from tz_canary import validate_time_zone

df = pd.read_csv("docs/data/example_data.csv", index_col="datetime", parse_dates=True)

validate_time_zone(df.index, "Europe/Amsterdam")  # will pass
validate_time_zone(df.index, "America/New_York")  # will raise ImplausibleTimeZoneError
validate_time_zone(df.index, "UTC")  # will raise ImplausibleTimeZoneError
```

### Time zone inference

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

### Advanced usage: inference with cached `TransitionsData`

When processing many time series, it can be useful to cache the transitions data used by `tz-canary` to infer time zones.
You can do this by creating a `TransitionsData` object and passing it to `infer_time_zone` (and this also works for `validate_time_zone`):

```python
import pandas as pd

from tz_canary import TransitionsData, infer_time_zone

# We create a TransitionsData object to avoid having to recompute the transitions for
#   every call to validate_time_zone.
transition_data = TransitionsData(2010, 2023)

for i in range(10):
    df = pd.read_csv(
        "docs/data/example_data.csv",  # In reality, these would be different files
        index_col="datetime",
        parse_dates=True,
    )
    plausible_time_zones = infer_time_zone(df.index, transition_data=transition_data)
    print(i, plausible_time_zones)
```

## Development

1. Make sure you have [git](https://git-scm.com/), [git LFS](https://git-lfs.com/), and [Poetry](https://python-poetry.org/) installed.
2. Clone this repository:
    ```bash
    git clone https://github.com/leonoverweel/tz-canary
    cd tz-canary
    ```
3. Install the development requirements:
    ```bash
    poetry install --with dev
    ```
4. Install the pre-commit hooks (used for linting):
    ```bash
    pre-commit install
    ```
5. Run the tests:
    ```bash
    poetry run pytest
    ```

### Making a release

1. Bump the version number in `pyproject.toml` and commit the change.
2. Make a [new release](https://github.com/leonoverweel/tz-canary/releases) on GitHub.
3. Build the package:
    ```bash
    poetry build
    ```
4. Publish the package to PyPI:
    ```bash
    poetry publish
    ```

## Contributing

Please don't hesitate to open issues and PRs!
