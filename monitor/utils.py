import datetime
import functools
import itertools
import operator
import re


now = datetime.datetime.utcnow


def compose(*fs):
    return functools.reduce(lambda f, g: lambda *args: f(g(*args)), fs)


def parse_timedelta(string):
    """
    Parses duration string, where the duration is given as a string consisting
    of at least one component. A valid component consists of at least one
    numeral immediately followed by a unit of time. Valid units of time are:
      - h  [hours]
      - m  [minutes]
      - s  [seconds]
      - ms [milliseconds]
      - us [microseconds]

    For instance, duration strings may look like this:
      - 1h 5m 19s
      - 1h5m19s
      - 2500ms
      - 2s500ms
      - 1234us 9h 10s 5ms (valid, albeit a bit confusing)
    """
    units = dict(
        microseconds="us",
        milliseconds="ms",
        seconds="s",
        minutes="m",
        hours="h",
    )

    def transform(name, unit):
        return fr"((?P<{name}>\d+){unit})"

    options = r"|".join(itertools.starmap(transform, units.items()))
    pattern = re.compile(fr"({options}|\s*)+")
    matches = pattern.match(string).groupdict()

    try:
        keys, values = zip(*filter(operator.itemgetter(1), matches.items()))
    except ValueError:
        # NOTE: Defaulting to zero if no valid components were given.
        return datetime.timedelta()
    return datetime.timedelta(**dict(zip(keys, map(int, values))))
