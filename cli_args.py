import argparse
import logging

from constants import GRPC_PORT_DEFAULT, HSV_RANGE_DEFAULT, SERIAL_PORT_DEFAULT, DEFAULT_BAUD
from constants import HTTP_DELAY_SECS_DEFAULT, HTTP_HOST_DEFAULT, HTTP_TEMPLATE_DEFAULT, CAMERA_NAME_DEFAULT
from constants import MINIMUM_PIXELS_DEFAULT, WIDTH_DEFAULT, MIDDLE_PERCENT_DEFAULT


def setup_cli_args(*args):
    parser = argparse.ArgumentParser()
    for arg in args:
        arg(parser)
    return vars(parser.parse_args())


def bgr(p):
    return p.add_argument("-b", "--bgr", dest="bgr_color", required=True, type=str,
                          help="BGR target value, e.g., -b \"174, 56, 5\"")


def usb(p):
    return p.add_argument("-u", "--usb", dest="usb_camera", default=False, required=False, action="store_true",
                          help="Use USB Raspi camera [false]")


def flip_x(p):
    return p.add_argument("-x", "--flipx", dest="flip_x", default=False, required=False, action="store_true",
                          help="Flip image on X axis[false]")


def flip_y(p):
    return p.add_argument("-y", "--flipy", dest="flip_y", default=False, action="store_true",
                          help="Flip image on Y axis[false]")


def width(p):
    return p.add_argument("-w", "--width", default=WIDTH_DEFAULT, type=int,
                          help="Image width [{0}]".format(WIDTH_DEFAULT))


def middle_percent(p):
    return p.add_argument("-e", "--percent", dest="middle_percent", default=MIDDLE_PERCENT_DEFAULT,
                          type=int, help="Middle percent [{0}]".format(MIDDLE_PERCENT_DEFAULT))


def minimum_pixels(p):
    return p.add_argument("-m", "--min", dest="minimum_pixels", default=MINIMUM_PIXELS_DEFAULT,
                          type=int,
                          help="Minimum pixel area [{0}]".format(MINIMUM_PIXELS_DEFAULT))


def hsv_range(p):
    return p.add_argument("-r", "--range", dest="hsv_range", default=HSV_RANGE_DEFAULT, type=int,
                          help="HSV range [{0}]".format(HSV_RANGE_DEFAULT))


def grpc_port(p):
    return p.add_argument("-p", "--port", dest="grpc_port", default=GRPC_PORT_DEFAULT, type=int,
                          help="gRPC port [{0}]".format(GRPC_PORT_DEFAULT))


def grpc_host(p):
    return p.add_argument("-g", "--grpc", dest="grpc_host", required=True,
                          help="gRPC location server hostname")


def leds(p):
    return p.add_argument("-l", "--leds", default=False, action="store_true",
                          help="Enable Blinkt led feedback [false]")


def display(p):
    return p.add_argument("-d", "--display", default=False, action="store_true", help="Display image [false]")


def serial_port(p):
    return p.add_argument("-s", "--serial", dest="serial_port", default=SERIAL_PORT_DEFAULT,
                          help="Serial port [{0}]".format(SERIAL_PORT_DEFAULT))


def baud_rate(p):
    return p.add_argument("--baud", dest="baud_rate", default=DEFAULT_BAUD,
                          help="Baud rate [{0}]".format(DEFAULT_BAUD))


def camera_name(p):
    return p.add_argument("-c", "--camera", dest="camera_name", required=True, help="Camera name")


def camera_name_optional(p):
    return p.add_argument("-c", "--camera", dest="camera_name", required=False,
                          default=CAMERA_NAME_DEFAULT, help="Camera name")


def mqtt_host(p):
    return p.add_argument("-m", "--mqtt", dest="mqtt_host", required=True, help="MQTT server hostname")


def calib(p):
    return p.add_argument("-c", "--calib", default=False, action="store_true", help="Calibration mode [false]")


def alternate(p):
    return p.add_argument("-a", "--alternate", default=False, action="store_true",
                          help="Alternate servo actions [false]")


def http_host(p):
    return p.add_argument("-t", "--http", dest="http_host", default=HTTP_HOST_DEFAULT, required=False,
                          help="HTTP hostname:port [{0}]".format(HTTP_HOST_DEFAULT))


def http_delay_secs(p):
    return p.add_argument("--delay", default=HTTP_DELAY_SECS_DEFAULT, type=float, dest="http_delay_secs",
                          help="HTTP delay secs [{0}]".format(HTTP_DELAY_SECS_DEFAULT))


def http_file(p):
    return p.add_argument("-i", "--file", default=HTTP_TEMPLATE_DEFAULT, type=str,
                          dest="http_file", help="HTTP template file")


def verbose_http(p):
    return p.add_argument("-o", "--verbose-http", default=False, action="store_true", dest="http_verbose",
                          help="Enable verbose HTTP log [false]")


def verbose(p):
    return p.add_argument("-v", "--verbose", dest="loglevel", default=logging.INFO, action="store_const",
                          const=logging.DEBUG, help="Enable debugging info")
