import pandas as pd
import pytest


@pytest.fixture
def idx_ams_2022():
    return pd.date_range(
        start="2022-01-01", end="2022-12-31 23:45:00", freq="15T", tz="Europe/Amsterdam"
    ).tz_localize(None)


@pytest.fixture
def idx_ams_2023():
    return pd.date_range(
        start="2023-01-01", end="2023-12-31 23:45:00", freq="15T", tz="Europe/Amsterdam"
    ).tz_localize(None)


@pytest.fixture
def idx_ny_2023():
    return pd.date_range(
        start="2023-01-01", end="2023-12-31 23:45:00", freq="15T", tz="America/New_York"
    ).tz_localize(None)


@pytest.fixture
def idx_utc_2023():
    return pd.date_range(
        start="2023-01-01", end="2023-12-31 23:45:00", freq="15T", tz="UTC"
    ).tz_localize(None)
