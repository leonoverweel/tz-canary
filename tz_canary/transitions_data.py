import pytz


class TransitionsData:
    def __init__(self, start_year=1970, end_year=2038):
        self.start_year = start_year
        self.end_year = end_year

        self.tz_transitions = None
        self.build_tz_transitions()

    def build_tz_transitions(self):
        self.tz_transitions = {}

        for tz_name in pytz.common_timezones:
            tz = pytz.timezone(tz_name)
            try:
                self.tz_transitions[tz_name] = [
                    (a, *b)
                    for a, b in zip(
                        tz._utc_transition_times,
                        tz._transition_info,
                    )
                    # TODO: Add check for between start_year and end_year
                ]
            except AttributeError:
                pass  # Not all time zones have _utc_transition_times


if __name__ == "__main__":
    transitions = TransitionsData()
    from pprint import pprint

    pprint(transitions.tz_transitions["Europe/Amsterdam"])
