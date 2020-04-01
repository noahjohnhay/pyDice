# coding=utf-8

import sys

from logbook import Logger, StreamHandler, compat
from py_dice import routes

if __name__ == "__main__":
    log = Logger(__name__)
    handler = StreamHandler(
        sys.stdout,
        level="INFO",
        format_string="{record.channel}: [{record.level_name}] {record.message}",
    )
    compat.redirect_logging()
    handler.push_application()
    routes.start_api()
