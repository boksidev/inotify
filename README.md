# inotify

This is a Docker container for triggering a command based on changes to a monitored directory.
Multiple monitors can be set up for different directories.

## Usage

### Run

```bash
docker create \
    --rm \
    --name inotifyc \
    -v /config/dir/path:/config:rw \
    -v /dir/path:/dir1 \
    $IMAGE
docker start inotifyc
```

In this case `IMAGE` is either the tag of an image you built yourself,
or the image hosted at [ghcr][1].

## Sample configuration

Below is a sample configuration file, which formats Python files with black.

```ini
# black.ini
[default]
mode=heap
debug=off
use_polling=no

[events]
command=black $FILE
modified=on
moved=on
created=on
deleted=off
closed=off

[acl]
uid=0
gid=0
umask=0000

[fs]
directory=/dir1
include=*.py
exclude=*.tmp
directory_events=off
check_existence=yes

[time]
debounce=100ms
period=50ms
timeout=5s
requeue=250ms
```

[1]: https://github.com/boksidev/inotify/pkgs/container/inotify
