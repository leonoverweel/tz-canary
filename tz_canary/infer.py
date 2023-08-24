import logging
from datetime import timedelta
from typing import Optional, Set
from zoneinfo import ZoneInfo

import pandas as pd

from tz_canary.transitions_data import Transition, TransitionsData


logger = logging.getLogger(__name__)


def infer_time_zone(
    dt_index: pd.DatetimeIndex, transition_data: Optional[TransitionsData] = None
) -> Set[ZoneInfo]:
    """Infer a set of plausible time zones based on DST switches.

    Args:
        dt_index: A pandas DatetimeIndex.
        transition_data: A TransitionsData object. If None, the TransitionsData will be
            built for the years spanning the given index. When inferring time zones for
            many indices, it is more efficient to pass a TransitionsData object that
            spans the entire time range.

    Returns:
        A set of plausible time zones for the given index.
    """

    if transition_data is None:
        transition_data = TransitionsData(
            year_start=dt_index.min().year, year_end=dt_index.max().year
        )

    # Remove time zone if set; what the index reports to be is irrelevant for inference.
    reported_tz = dt_index.tz
    if reported_tz is not None:
        logger.info(
            f"`dt_index` claims to have time zone `{reported_tz}`. "
            "Ignoring this during time zone inference."
        )
        dt_index = dt_index.tz_localize(None)

    # Find plausible time zones
    # TODO - Once we also have fall DST checks, start from the full set and remove
    #   implausible time zones instead of starting from an empty set and adding
    #   plausible ones.
    plausible_time_zones = set()
    for tz_name, transitions in transition_data.tz_transitions.items():
        transition_occurrences = [
            _check_transition_occurs(dt_index, tz_name, transition)
            for transition in transitions
        ]
        if any(transition_occurrences):
            plausible_time_zones.add(ZoneInfo(tz_name))

    return plausible_time_zones


def _check_transition_occurs(
    dt_index_naive: pd.DatetimeIndex, candidate_tz_name: str, transition: Transition
) -> Optional[bool]:
    """Check if a DST transition occurs in the given index.

    We check three cases:
    - Whether the transition time is within the index at all
    - Whether a spring forward DST transition occurs (if applicable to the transition)
    - Whether a fall backwards DST transition occurs (if applicable to the transition)

    Args:
        dt_index_naive: A time zone-naive datetime index.
        candidate_tz_name: The name of the time zone whose transition we're checking.
        transition: The transition to check.

    Returns:
        True if the transition occurs, False if it does not, None if it is outside the
            range of the index.
    """
    if dt_index_naive.tz is not None:
        raise ValueError(
            "`dt_index_naive` may not have a time zone set. "
            "You can remove it using `.tz_localize(None)`"
        )

    # If the transition time is not within the index, it cannot have occurred.
    utc_transition_time_naive = transition.utc_transition_time.replace(tzinfo=None)
    if (
        utc_transition_time_naive < dt_index_naive.min()
        or utc_transition_time_naive > dt_index_naive.max()
    ):
        return None

    # Check if the transition occurs (spring forward or fall back).
    if _check_spring_forward_occurs(dt_index_naive, transition, candidate_tz_name):
        return True
    # TODO - implement check for fall back

    # Neither spring forward nor fall back occurred.
    return False


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
    #   the time zone information, so we can find it within the naive datetime index.
    local_transition_time_naive = transition.utc_transition_time.astimezone(
        ZoneInfo(candidate_tz_name)
    ).replace(tzinfo=None)

    # Find the indices in that are within the DST offset.
    idx_during_transition = dt_index_naive[
        (dt_index_naive < local_transition_time_naive)
        & (dt_index_naive > local_transition_time_naive - transition.dst_offset)
    ]

    # If there are no indices during the DST transition, a spring forward occurred. If
    #   there are, it did not.
    return len(idx_during_transition) == 0
