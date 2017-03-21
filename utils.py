import logging
import platform
import sys
import time


def add_http_prefix(url):
    return url if url.startswith("http://") or url.startswith("https://") else "http://" + url

def mqtt_broker_info(val):
    # Broker hostname can be either "localhost" or "localhost:999"
    return (val[:val.index(":")], int(val[val.index(":") + 1:])) if ":" in val else (val, 1883)


def is_raspi():
    return platform.system() == "Linux"


def is_windows():
    return sys.platform == "win32"


def is_python3():
    return sys.version_info[0] >= 3


def sleep():
    while True:
        time.sleep(60)


def current_time_millis():
    return int(round(time.time() * 1000))


def strip_args(args, *excludes):
    return {k: args[k] for k in args.keys() if k not in excludes}


def strip_loglevel(args):
    return {k: args[k] for k in args.keys() if k != "loglevel"}


def setup_logging(filename=None,
                  filemode="a",
                  stream=sys.stderr,
                  level=logging.INFO,
                  format="%(asctime)s %(name)-10s %(funcName)-10s():%(lineno)i: %(levelname)-6s %(message)s"):
    if filename:
        logging.basicConfig(filename=filename, filemode=filemode, level=level, format=format)
    else:
        logging.basicConfig(stream=stream, level=level, format=format)


# As described at http://legacy.python.org/dev/peps/pep-0469/

try:
    dict.iteritems
except AttributeError:
    # Python 3
    def itervalues(d):
        return iter(d.values())


    def iteritems(d):
        return iter(d.items())


    def listvalues(d):
        return list(d.values())


    def listitems(d):
        return list(d.items())
else:
    # Python 2
    def itervalues(d):
        return d.itervalues()


    def iteritems(d):
        return d.iteritems()


    def listvalues(d):
        return d.values()


    def listitems(d):
        return d.items()
