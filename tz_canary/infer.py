import logging
from datetime import datetime, timedelta
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
            many indices, it is more efficient to build a TransitionsData object once
            and pass it to multiple calls of this function.

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

    # Find plausible time zones.
    all_time_zones = set(ZoneInfo(tz) for tz in transition_data.tz_transitions.keys())
    plausible_time_zones = set()  # all expected DST transitions occur
    implausible_time_zones = set()  # at least one expected DST transition doesn't occur

    for tz_name, transitions in transition_data.tz_transitions.items():
        # Check if each transition occurs, does not occur, or is out of range.
        transition_occurrences = [
            _check_transition_occurs(dt_index, tz_name, transition)
            for transition in transitions
        ]

        # Discard out-of-range transitions as they do not give us any information.
        transition_occurrences_within_range = [
            t for t in transition_occurrences if t is not None
        ]

        # If no transitions occur with in the range, we cannot say whether the time zone
        #   is plausible or not.
        if len(transition_occurrences_within_range) == 0:
            continue

        # If all DST changes that are expected for the time zone occur it is a plausible
        #   time zone. Otherwise, it is not.
        if all(transition_occurrences_within_range):
            plausible_time_zones.add(ZoneInfo(tz_name))
        else:
            implausible_time_zones.add(ZoneInfo(tz_name))

    # If there are no plausible time zones specifically detected for the index (its
    #   range may not cover any potential DST changes, or it may actually have no DST
    #   changes), we say all time zones that are not implausible are plausible.
    if len(plausible_time_zones) == 0:
        plausible_time_zones = all_time_zones - implausible_time_zones

    return plausible_time_zones


def _check_transition_occurs(
    dt_index_naive: pd.DatetimeIndex, candidate_tz_name: str, transition: Transition
) -> Optional[bool]:
    """Check if a DST transition occurs in the given index.

    We check three cases:
    - Whether the transition time is within the index at all
    - Whether a spring forward DST transition occurs (if applicable to the transition)
    - Whether a fall back DST transition occurs (if applicable to the transition)

    Args:
        dt_index_naive: A time-zone-naive datetime index.
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
    if _check_fall_back_occurs(dt_index_naive, transition, candidate_tz_name):
        return True

    # Neither spring forward nor fall back occurred.
    return False


def _check_spring_forward_occurs(
    dt_index_naive: pd.DatetimeIndex, transition: Transition, candidate_tz_name: str
) -> bool:
    """Check if the transition from non-DST to DST occurs (spring forward).

    When converting the UTC transition time to the new time zone, the hour (to be
    precise, the amount of time corresponding to the DST offset) before it should not
    exist in the index.

    Args:
        dt_index_naive: A time-zone-naive datetime index.
        transition: The potential spring forward transition to check.
        candidate_tz_name: The name of the time zone whose transition we're checking.

    Returns:
        True if the spring forward DST transition occurs, False if it does not.
    """

    # When we spring forward, the DST offset is positive; if it is negative, a spring
    #   forward definitely did not occur.
    if transition.dst_offset <= timedelta(0):
        return False

    # First localize the UTC transition time to the new candidate time zone, then remove
    #   the time zone information, so we can find it within the naive datetime index.
    local_transition_time_naive = _localize_naive(
        utc_time=transition.utc_transition_time, tz_name=candidate_tz_name
    )

    # Find the indices in that are within the DST offset.
    idx_during_transition = dt_index_naive[
        (dt_index_naive < local_transition_time_naive)
        & (dt_index_naive > local_transition_time_naive - transition.dst_offset)
    ]

    # If there are no indices during the DST transition, a spring forward occurred. If
    #   there are, it did not.
    return len(idx_during_transition) == 0


def _check_fall_back_occurs(
    dt_index_naive: pd.DatetimeIndex, transition: Transition, candidate_tz_name: str
) -> bool:
    """Check if the transition from DST to non-DST occurs (fall back).

    When converting the UTC transition time to the new time zone, this time should exist
    in the index twice: once with the DST offset, once without.

    Args:
        dt_index_naive: A time-zone-naive datetime index.
        transition: The potential fall back transition to check.
        candidate_tz_name: The name of the time zone whose transition we're checking.

    Returns:
        True if the fall back DST transition occurs, False if it does not.
    """

    # When we fall back, the DST offset becomes zero.
    if transition.dst_offset != timedelta(0):
        return False

    # Find the indices in that are equal to the localized, naive transition time.
    idx_during_transition = dt_index_naive[
        dt_index_naive
        == _localize_naive(transition.utc_transition_time, candidate_tz_name)
    ]

    # If there are two indices at the time of the DST transition, a fall back occurred.
    #   If not, it did not.
    return len(idx_during_transition) == 2


def _localize_naive(utc_time: datetime, tz_name: str) -> datetime:
    """Localize a time-zone-aware UTC time to a time zone and make it time-zone-naive.

    Args:
        utc_time: A time-zone-aware time in UTC.
        tz_name: The name of the time zone to localize to.

    Returns:
        The naive localized time.
    """

    return utc_time.astimezone(ZoneInfo(tz_name)).replace(tzinfo=None)
