import functools
import logging
import operator
from watchdog import events
from monitor import collections, utils


class EventHandler(events.PatternMatchingEventHandler):
    def __init__(self, config, queue):
        super().__init__(
            patterns=config.fs.include,
            ignore_patterns=config.fs.exclude,
            ignore_directories=not config.fs.directory_events,
        )
        self.config = config
        self.queue = queue
        self.scheduled = dict()

        if config.events.moved:
            self.on_moved = self._on_event
        if config.events.created:
            self.on_created = self._on_event
        if config.events.deleted:
            self.on_deleted = self._on_event
        if config.events.modified:
            self.on_modified = self._on_event
        if config.events.closed:
            self.on_closed = self._on_event

    def schedule(self, item):
        self.scheduled[item.path] = utils.now()

    def _on_event(self, event):
        item = collections.Item.fromevent(event)

        too_soon = utils.compose(
            functools.partial(operator.gt, self.config.time.requeue),
            functools.partial(operator.sub, item.timestamp),
        )

        if (timestamp := self.scheduled.get(item.path)) and too_soon(timestamp):
            return logging.debug(f"avoiding requeue on {item.path}")

        self.queue.push(item)
