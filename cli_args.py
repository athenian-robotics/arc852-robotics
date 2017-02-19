import argparse
import logging

from constants import CAMERA_NAME, CAMERA_NAME_DEFAULT, MQTT_HOST, SERIAL_PORT, BAUD_RATE, HTTP_HOST, DEVICE_ID, \
    LED_NAME, LED_BRIGHTNESS_DEFAULT, LED_BRIGHTNESS
from constants import DRAW_CONTOUR, DRAW_BOX
from constants import HSV_RANGE, WIDTH, USB_CAMERA, BGR_COLOR, MIDDLE_PERCENT, FLIP_X, FLIP_Y
from constants import HSV_RANGE_DEFAULT, SERIAL_PORT_DEFAULT, DEFAULT_BAUD, GRPC_PORT_DEFAULT, GRPC_HOST, MQTT_TOPIC
from constants import HTTP_DELAY_SECS, HTTP_FILE, LOG_LEVEL, LOG_FILE, MINIMUM_PIXELS, GRPC_PORT, DISPLAY, LEDS
from constants import HTTP_DELAY_SECS_DEFAULT, HTTP_HOST_DEFAULT, HTTP_TEMPLATE_DEFAULT
from constants import MINIMUM_PIXELS_DEFAULT, WIDTH_DEFAULT, MIDDLE_PERCENT_DEFAULT


def setup_cli_args(*args):
    parser = argparse.ArgumentParser()
    for arg in args:
        arg(parser)
    return vars(parser.parse_args())


def bgr(p):
    return p.add_argument("--bgr", "--bgr_color", dest=BGR_COLOR, required=True,
                          help="BGR target value, e.g., -b \"174, 56, 5\"")


def usb(p):
    return p.add_argument("-u", "--usb", dest=USB_CAMERA, default=False, action="store_true",
                          help="Use USB Raspi camera [false]")


def flip_x(p):
    return p.add_argument("-x", "--flipx", dest=FLIP_X, default=False, action="store_true",
                          help="Flip image on X axis[false]")


def flip_y(p):
    return p.add_argument("-y", "--flipy", dest=FLIP_Y, default=False, action="store_true",
                          help="Flip image on Y axis[false]")


def width(p):
    return p.add_argument("-w", "--width", dest=WIDTH, default=WIDTH_DEFAULT, type=int,
                          help="Image width [{0}]".format(WIDTH_DEFAULT))


def middle_percent(p):
    return p.add_argument("--percent", "--middle_percent", dest=MIDDLE_PERCENT, default=MIDDLE_PERCENT_DEFAULT,
                          type=int, help="Middle percent [{0}]".format(MIDDLE_PERCENT_DEFAULT))


def minimum_pixels(p):
    return p.add_argument("--min", "--min_pixels", dest=MINIMUM_PIXELS, default=MINIMUM_PIXELS_DEFAULT,
                          type=int,
                          help="Minimum pixel area [{0}]".format(MINIMUM_PIXELS_DEFAULT))


def hsv_range(p):
    return p.add_argument("--range", "--hsv_range", dest=HSV_RANGE, default=HSV_RANGE_DEFAULT, type=int,
                          help="HSV range [{0}]".format(HSV_RANGE_DEFAULT))


def grpc_port(p):
    return p.add_argument("-p", "--port", dest=GRPC_PORT, default=GRPC_PORT_DEFAULT, type=int,
                          help="gRPC port [{0}]".format(GRPC_PORT_DEFAULT))


def grpc_host(p):
    return p.add_argument("-g", "--grpc", "--grpc_host", dest=GRPC_HOST, required=True,
                          help="gRPC location server hostname")


def leds(p):
    return p.add_argument("--leds", dest=LEDS, default=False, action="store_true",
                          help="Enable Blinkt led feedback [false]")


def draw_contour(p):
    return p.add_argument("--draw_contour", "--contour", dest=DRAW_CONTOUR, default=False, action="store_true",
                          help="Draw contour box [false]")


def draw_box(p):
    return p.add_argument("--draw_box", "--box", dest=DRAW_BOX, default=False, action="store_true",
                          help="Draw bounding box [false]")


def display(p):
    return p.add_argument("--display", dest=DISPLAY, default=False, action="store_true", help="Display image [false]")


def serial_port(p):
    return p.add_argument("-s", "--serial", dest=SERIAL_PORT, default=SERIAL_PORT_DEFAULT,
                          help="Serial port [{0}]".format(SERIAL_PORT_DEFAULT))


def baud_rate(p):
    return p.add_argument("--baud", "--baud_rate", dest=BAUD_RATE, default=DEFAULT_BAUD,
                          help="Baud rate [{0}]".format(DEFAULT_BAUD))


def device_id(p):
    return p.add_argument("--did", "--device_id", dest=DEVICE_ID, help="USB device ID")


def led_name(p):
    return p.add_argument("--led", "--led_name", dest=LED_NAME, required=True, help="LED name")


def led_brightness(p):
    return p.add_argument("--brightness", "--led_brightness", dest=LED_BRIGHTNESS, default=LED_BRIGHTNESS_DEFAULT,
                          help="LED brightness [{0}]".format(LED_BRIGHTNESS_DEFAULT))


def camera_name(p):
    return p.add_argument("-c", "--camera", "--camera_name", dest=CAMERA_NAME, required=True, help="Camera name")


def camera_name_optional(p):
    return p.add_argument("-c", "--camera", "--camera_name", dest=CAMERA_NAME, required=False,
                          default=CAMERA_NAME_DEFAULT, help="Camera name")


def mqtt_host(p):
    return p.add_argument("-m", "--mqtt", "--mqtt_host", dest=MQTT_HOST, required=True, help="MQTT server hostname")


def calib(p):
    return p.add_argument("--calib", default=False, action="store_true", help="Calibration mode [false]")


def alternate(p):
    return p.add_argument("--alternate", default=False, action="store_true",
                          help="Alternate servo actions [false]")


def http_host(p):
    return p.add_argument("--http", dest=HTTP_HOST, default=HTTP_HOST_DEFAULT,
                          help="HTTP hostname:port [{0}]".format(HTTP_HOST_DEFAULT))


def http_delay_secs(p):
    return p.add_argument("--delay", dest=HTTP_DELAY_SECS, default=HTTP_DELAY_SECS_DEFAULT, type=float,
                          help="HTTP delay secs [{0}]".format(HTTP_DELAY_SECS_DEFAULT))


def http_file(p):
    return p.add_argument("-i", "--file", dest=HTTP_FILE, default=HTTP_TEMPLATE_DEFAULT,
                          help="HTTP template file")


def verbose_http(p):
    return p.add_argument("--verbose-http", dest="http_verbose", default=False, action="store_true",
                          help="Enable verbose HTTP log [false]")


def verbose(p):
    return p.add_argument("-v", "--verbose", dest=LOG_LEVEL, default=logging.INFO, action="store_const",
                          const=logging.DEBUG, help="Enable debugging info")

def log_file(p):
    return p.add_argument("-l", "--log-file", dest=LOG_FILE, default=None,
                          help="Logging output to file")

def mqtt_topic(p):
    return p.add_argument("--topic", "--mqtt-topic", dest=MQTT_TOPIC, required=True,
                          help="Desired MQTT topic")