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
