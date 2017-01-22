import platform
import sys
import time


def mqtt_broker_info(val):
    # Broker hostname can be either "localhost" or "localhost:999"
    return (val[:val.index(":")], int(val[val.index(":") + 1:])) if ":" in val else (val, 1883)


def is_raspi():
    return platform.system() == "Linux"


def is_python3():
    return sys.version_info[0] >= 3


def sleep():
    while True:
        time.sleep(60)
