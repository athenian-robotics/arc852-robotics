import argparse
import logging


def setup_cli_args(*args):
    parser = argparse.ArgumentParser()
    for arg in args:
        arg(parser)
    return vars(parser.parse_args())


def bgr(parser):
    parser.add_argument("-b", "--bgr", type=str, required=True, help="BGR target value, e.g., -b \"174, 56, 5\"")


def usb(parser):
    parser.add_argument("-u", "--usb", default=False, action="store_true", help="Use USB Raspi camera [false]")


def flip(parser):
    parser.add_argument("-f", "--flip", default=False, action="store_true", help="Flip image [false]")


def width(parser):
    parser.add_argument("-w", "--width", default=400, type=int, help="Image width [400]")


def percent(parser):
    parser.add_argument("-e", "--percent", default=15, type=int, help="Middle percent [15]")


def min(parser):
    parser.add_argument("-m", "--min", default=100, type=int, help="Minimum pixel area [100]")


def range(parser):
    parser.add_argument("-r", "--range", default=20, type=int, help="HSV range")


def port(parser):
    parser.add_argument("-p", "--port", default=50051, type=int, help="gRPC port [50051]")


def leds(parser):
    parser.add_argument("-l", "--leds", default=False, action="store_true",
                        help="Enable Blinkt led feedback [false]")


def display(parser):
    parser.add_argument("-d", "--display", default=False, action="store_true", help="Display image [false]")


def verbose(parser):
    parser.add_argument("-v", "--verbose", default=logging.INFO, help="Include debugging info",
                        action="store_const", dest="loglevel", const=logging.DEBUG)


def grpc(parser):
    parser.add_argument("-g", "--grpc", required=True, help="gRPC location server hostname")


def camera(parser):
    parser.add_argument("-c", "--camera", required=True, help="Camera name")


def camera_optional(parser):
    parser.add_argument("-c", "--camera", required=False, help="Camera name")


def mqtt(parser):
    parser.add_argument("-m", "--mqtt", required=True, help="MQTT server hostname")


def calib(parser):
    parser.add_argument("-c", "--calib", default=False, action="store_true", help="Calibration mode [false]")


def alternate(parser):
    parser.add_argument("-a", "--alternate", default=False, action="store_true", help="Alternate servo actions [false]")


def http_enable(parser):
    parser.add_argument("-t", "--http", default=False, action="store_true", help="Enable HTTP server [false]")


def http_host(parser):
    parser.add_argument("-o", "--host", default="localhost", required=False, help="HTTP hostname [localhost]")


def http_pause(parser):
    parser.add_argument("-s", "--pause", default=0.5, type=float, help="HTTP pause secs [0.5]")
