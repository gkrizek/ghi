import logging
import sys


class SystemdHandler(logging.Handler):
    PREFIX = {
        # EMERG <0>
        # ALERT <1>
        logging.CRITICAL: "<2>",
        logging.ERROR: "<3>",
        logging.WARNING: "<4>",
        # NOTICE <5>
        logging.INFO: "<6>",
        logging.DEBUG: "<7>",
        logging.NOTSET: "<7>"
    }

    def __init__(self, stream=sys.stdout):
        self.stream = stream
        logging.Handler.__init__(self)

    def emit(self, record):
        try:
            msg = self.PREFIX[record.levelno] + self.format(record) + "\n"
            self.stream.write(msg)
            self.stream.flush()
        except Exception: 
            self.handleError(record)


def setup_server_logging(mode, debug=None):
    root_logger = logging.getLogger()
    root_logger.setLevel("INFO")
    mode = mode.lower() 

    # AWS Lambda configures the logger before executing this script
    # We want to remove their configurations and set our own
    log = logging.getLogger()
    if log.handlers:
        for handler in log.handlers:
            log.removeHandler(handler)

    if mode == 'systemd':
        # replace handler with systemd one
        root_logger.addHandler(SystemdHandler())
    if mode == 'aws':
        logging.basicConfig(
                level=logging.INFO,
                format="%(message)s"
            )
    if mode == 'plain':
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [ghi] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    if debug:
        # Enable debug if set in config
        logging.getLogger().setLevel(logging.DEBUG)
