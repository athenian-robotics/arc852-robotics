import logging
import sys

TOPIC = "topic"
CAMERA_NAME = "camera_name"

LOGGING_ARGS = {"stream": sys.stderr,
                "level": logging.INFO,
                "format": "%(asctime)s %(name)-10s %(funcName)-10s():%(lineno)i: %(levelname)-6s %(message)s"}


def logging_args(level):
    return {"stream": sys.stderr,
            "level": level,
            "format": "%(asctime)s %(name)-10s %(funcName)-10s():%(lineno)i: %(levelname)-6s %(message)s"}
