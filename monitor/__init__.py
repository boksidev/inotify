import logging
from watchdog import observers
from monitor import collections, configuration, dispatch, handlers


def main(args):
    config = configuration.Configuration.fromfile(args.config)

    logging.basicConfig(
        level=logging.DEBUG if config.default.debug else logging.INFO,
        format=f"[%(asctime)s] <%(levelname)s> {args.config.stem}: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.info("CONFIGURATION:")
    logging.info("             MODE=%s", config.default.mode)
    logging.info("            DEBUG=%s", config.default.debug)
    logging.info("      USE_POLLING=%s", config.default.use_polling)
    logging.info("EVENTS:")
    logging.info("          COMMAND=%s", config.events.command)
    logging.info("         MODIFIED=%s", config.events.modified)
    logging.info("          CREATED=%s", config.events.created)
    logging.info("          DELETED=%s", config.events.deleted)
    logging.info("            MOVED=%s", config.events.moved)
    logging.info("           CLOSED=%s", config.events.closed)
    logging.info("FS:")
    logging.info("        DIRECTORY=%s", config.fs.directory)
    logging.info("          INCLUDE=%s", config.fs.include)
    logging.info("          EXCLUDE=%s", config.fs.exclude)
    logging.info(" DIRECTORY_EVENTS=%s", config.fs.directory_events)
    logging.info("  CHECK_EXISTENCE=%s", config.fs.check_existence)
    logging.info("ACL:")
    logging.info("              UID=%s", config.acl.uid)
    logging.info("              GID=%s", config.acl.gid)
    logging.info("            UMASK=%s", config.acl.umask)
    logging.info("TIME:")
    logging.info("         DEBOUNCE=%s", config.time.debounce)
    logging.info("           PERIOD=%s", config.time.period)
    logging.info("          REQUEUE=%s", config.time.requeue)
    logging.info("          TIMEOUT=%s", config.time.timeout)

    logging.info(f"Starting monitor for {args.config.stem}")

    if config.default.use_polling:
        logging.info("Using polling to detect changes")
        observer = observers.polling.PollingObserver()
    else:
        logging.info("Using native change detection to detect changes")
        observer = observers.Observer()

    dispatcher = dispatch.Dispatcher(
        acl=config.acl,
        command=config.events.command,
        timeout=config.time.timeout,
        check_existence=config.fs.check_existence,
    )
    queue = collections.Queue(
        period=config.time.period,
        debounce=config.time.debounce,
    )
    handler = handlers.EventHandler(config=config, queue=queue)

    observer.schedule(handler, path=config.fs.directory, recursive=True)
    observer.start()

    try:
        for item in queue:
            handler.schedule(item)
            dispatcher.process(item=item)

    except KeyboardInterrupt:
        observer.stop()

    observer.join()
