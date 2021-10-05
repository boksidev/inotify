import dataclasses
import datetime
import functools
import heapq
import time
import threading
from watchdog import events
from monitor import utils


@dataclasses.dataclass(order=True)
class Item:
    timestamp: datetime.datetime
    event: events.FileSystemEvent = dataclasses.field(compare=False)

    @property
    def path(self):
        if self.event.event_type == events.EVENT_TYPE_MOVED:
            return self.event.dest_path
        return self.event.src_path

    @classmethod
    def fromevent(cls, event):
        return cls(timestamp=utils.now(), event=event)


class Queue:
    def __init__(self, period, debounce):
        seconds = period.total_seconds() if period else 0
        self.wait = functools.partial(time.sleep, seconds)
        self.debounce = debounce
        self._heap = list()
        self._map = dict()
        self._lock = threading.RLock()

    def push(self, item):
        with self._lock:
            if previous := self._map.get(item.path):
                previous.timestamp = max(previous.timestamp, item.timestamp)
                heapq.heapify(self._heap)
            else:
                heapq.heappush(self._heap, item)
                self._map[item.path] = item

    def pop(self):
        with self._lock:
            item = heapq.heappop(self._heap)
            self._map.pop(item.path)
        return item

    def __iter__(self):
        return self

    def __next__(self):
        while not self._heap:
            self.wait()
        while utils.now() - (item := self.pop()).timestamp < self.debounce:
            self.push(item)
            self.wait()
        return item
