from datetime import datetime

import pytz


class TransitionsData:
    def __init__(self, year_start: int = 1970, year_end: int = 2038):
        self.year_start = year_start
        self.year_end = year_end

        self.tz_transitions = None
        self.build_tz_transitions()

    def build_tz_transitions(self):
        def _extract_tz_transition_info(transition_time, transition_info):
            return {
                "utc_transition_time": transition_time,  # when the switch happens
                "utc_offset": transition_info[0],  # the new UTC offset
                "dst": transition_info[1],  # not sure what this means
                "tz_name": transition_info[2],  # the new timezone name
            }

        self.tz_transitions = {}
        for iana_name in pytz.common_timezones:  # IANA: https://www.iana.org/time-zones
            tz = pytz.timezone(iana_name)
            try:
                self.tz_transitions[iana_name] = [
                    _extract_tz_transition_info(transition_time, transition_info)
                    for transition_time, transition_info in zip(
                        tz._utc_transition_times, tz._transition_info
                    )
                    if self.year_start <= transition_time.year <= self.year_end
                ]
            except AttributeError:
                pass  # Not all time zones have DST transitions


if __name__ == "__main__":
    transition_data = TransitionsData()
    from pprint import pprint

    pprint(transition_data.tz_transitions["Europe/Amsterdam"])
