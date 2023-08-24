from datetime import timedelta
from typing import Set
from zoneinfo import ZoneInfo

import pandas as pd

from tz_canary.transitions_data import Transition, TransitionsData


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
        if any(_check_transition_occurs(dt_index, tz_name, t) for t in transitions):
            plausible_tz.add(ZoneInfo(tz_name))

    return plausible_tz


def _check_transition_occurs(
    dt_index: pd.DatetimeIndex, candidate_tz_name: str, transition: Transition
) -> bool:
    # Range check with naive datetimes since real time zones are not yet known.
    dt_index_naive = dt_index.tz_localize(None)
    if (
        transition.utc_transition_time.replace(tzinfo=None) < dt_index_naive.min()
        or transition.utc_transition_time.replace(tzinfo=None) > dt_index_naive.max()
    ):
        return False

    # Cases
    if _check_spring_forward_occurs(dt_index_naive, transition, candidate_tz_name):
        return True

    return True


def _check_spring_forward_occurs(
    dt_index_naive: pd.DatetimeIndex, transition: Transition, candidate_tz_name: str
):
    """Check if the transition from non-DST to DST occurs (spring forward.

    When converting the UTC transition time to the new time zone, the hour (to be
    precise, the amount of time corresponding to the DST offset) before it should not
    exist in the index.
    """

    # When we spring forward, the DST offset is positive; if it is negative, a spring
    #   forward definitely did not occur.
    if transition.dst_offset <= timedelta(0):
        return False

    # First localize the UTC transition time to the new candidate time zone, then remove
    #   the time zone information so we can find it within the naive datetime index.
    local_transition_time = transition.utc_transition_time.astimezone(
        ZoneInfo(candidate_tz_name)
    )
    local_transition_time_naive = local_transition_time.replace(tzinfo=None)

    # Find the indices in that are within the DST offset.
    idx_during_transition = dt_index_naive[
        (dt_index_naive < local_transition_time_naive)
        & (dt_index_naive > local_transition_time_naive - transition.dst_offset)
    ]

    # If there are no indices during the DST transition, a spring forward occurred. If
    #   there are, it did not.
    return len(idx_during_transition) == 0
