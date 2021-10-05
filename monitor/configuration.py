import configparser
import dataclasses
import datetime
import enum
import functools
import operator
import pathlib
from monitor import utils


_DELTA = datetime.timedelta(seconds=1)


# TODO: Fix when implementing proper schedulers
class Mode(enum.Enum):
    heap = "heap"
    simple = "simple"


class Section:
    SECTION = None

    @classmethod
    def withdefaults(cls):
        transform = operator.attrgetter("name", "default")
        return cls(**dict(map(transform, dataclasses.fields(cls))))

    @classmethod
    def fromparser(cls, parser):
        if not parser.has_section(cls.SECTION):
            return cls.withdefaults()

        converters = {
            str: parser.get,
            int: parser.getint,
            bool: parser.getboolean,
            list: parser.getlist,
            datetime.timedelta: parser.gettimedelta,
            pathlib.Path: parser.getpath,
            Mode: parser.getmode,
        }

        def get_default(field):
            if field.default is not dataclasses.MISSING:
                return field.default
            if field.default_factory is not dataclasses.MISSING:
                return field.default_factory()
            raise ValueError("no default set")

        def transform(field):
            converter = functools.partial(converters.get(field.type), cls.SECTION)

            try:
                fallback = get_default(field)
                converter = functools.partial(converter, fallback=fallback)
            except ValueError:
                pass

            return field.name, converter(field.name)

        return cls(**dict(map(transform, dataclasses.fields(cls))))


@dataclasses.dataclass
class Default(Section):
    mode: Mode = dataclasses.field(default=Mode.heap)
    use_polling: bool = dataclasses.field(default=False)
    debug: bool = dataclasses.field(default=False)

    SECTION = "default"


@dataclasses.dataclass
class Events(Section):
    command: str = dataclasses.field(default=None)
    moved: bool = dataclasses.field(default=False)
    deleted: bool = dataclasses.field(default=False)
    created: bool = dataclasses.field(default=False)
    modified: bool = dataclasses.field(default=False)
    closed: bool = dataclasses.field(default=False)

    SECTION = "events"


@dataclasses.dataclass
class ACL(Section):
    uid: str = dataclasses.field(default="0")
    gid: str = dataclasses.field(default="0")
    umask: str = dataclasses.field(default="0")

    SECTION = "acl"


@dataclasses.dataclass
class FileSystem(Section):
    directory: pathlib.Path
    include: list = dataclasses.field(default=None)
    exclude: list = dataclasses.field(default=None)
    directory_events: bool = dataclasses.field(default=True)
    check_existence: bool = dataclasses.field(default=False)

    SECTION = "fs"


@dataclasses.dataclass
class Time(Section):
    debounce: datetime.timedelta = dataclasses.field(default=_DELTA)
    period: datetime.timedelta = dataclasses.field(default=None)
    timeout: datetime.timedelta = dataclasses.field(default=None)
    requeue: datetime.timedelta = dataclasses.field(default=_DELTA)

    SECTION = "time"


@dataclasses.dataclass
class Configuration:
    default: Default
    events: Events
    acl: ACL
    fs: FileSystem
    time: Time

    @classmethod
    def fromfile(cls, path):
        parser = configparser.ConfigParser(
            converters=dict(
                list=str.split,
                timedelta=utils.parse_timedelta,
                path=pathlib.Path,
                mode=Mode,
            ),
        )
        parser.read(path)

        def transform(field):
            return field.name, field.type.fromparser(parser)

        return cls(**dict(map(transform, dataclasses.fields(cls))))
