import logging
import pathlib
import subprocess


class Dispatcher:
    def __init__(self, *, acl, command, timeout, check_existence):
        self.args = "/files/runas.sh", acl.uid, acl.gid, acl.umask, command
        self.command = command
        self.timeout = timeout.total_seconds() if timeout else None
        self.check_existence = check_existence

    def process(self, item):
        if self.check_existence and not pathlib.Path(item.path).exists():
            return logging.debug(f"{item.path} does not exist, ignoring")

        logging.debug(f"Running command :: {self.command}")
        logging.debug(f"        timeout :: {self.timeout}")
        logging.debug(f"            env :: FILE={item.path}")

        logging.info("┌──────────────────────────────────────────────────────┐")

        env = dict(FILE=item.path)
        code = subprocess.call(self.args, env=env, timeout=self.timeout)

        logging.info("└──────────────────────────────────────────────────────┘")
        logging.info("Finished command. Exit code was %i.", code)
