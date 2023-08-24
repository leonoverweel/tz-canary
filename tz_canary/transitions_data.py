from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytz


@dataclass
class Transition:
    utc_transition_time: datetime  # When the transition occurs, in UTC
    utc_offset: timedelta  # The new UTC offset (e.g. 2h for CET -> CEST)
    dst_offset: timedelta  # The new amount of DST in effect (e.g. 1h for CET -> CEST)
    tz_name: str  # The new timezone name (e.g. CEST)

    @classmethod
    def from_pytz_transition(cls, transition_time, transition_info):
        return cls(
            utc_transition_time=transition_time.replace(tzinfo=ZoneInfo("UTC")),
            utc_offset=transition_info[0],
            dst_offset=transition_info[1],
            tz_name=transition_info[2],
        )


class TransitionsData:
    def __init__(self, year_start: int = 1970, year_end: int = 2038):
        self.year_start = year_start
        self.year_end = year_end

        self.tz_transitions = None
        self.build_tz_transitions()

    def build_tz_transitions(self):
        self.tz_transitions = {}
        for iana_name in pytz.common_timezones:  # IANA: https://www.iana.org/time-zones
            try:
                pytz_transitions = zip(
                    pytz.timezone(iana_name)._utc_transition_times,
                    pytz.timezone(iana_name)._transition_info,
                )
            except AttributeError:  # Not all time zones have DST transitions
                continue

            # Add transitions for this time zone for the given year range
            self.tz_transitions[iana_name] = [
                Transition.from_pytz_transition(transition_time, transition_info)
                for transition_time, transition_info in pytz_transitions
                if self.year_start <= transition_time.year <= self.year_end
            ]

        # Special case: UTC has no transitions
        self.tz_transitions["UTC"] = []


if __name__ == "__main__":
    transition_data = TransitionsData()
    from pprint import pprint

    pprint(transition_data.tz_transitions["Europe/Amsterdam"])
