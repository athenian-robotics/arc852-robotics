import argparse
import logging

import grpc_support
from  image_server import http_file_default


def setup_cli_args(*args):
    parser = argparse.ArgumentParser()
    for arg in args:
        arg(parser)
    return vars(parser.parse_args())


def bgr(parser):
    parser.add_argument("-b", "--bgr", dest="bgr_color", required=True, type=str,
                        help="BGR target value, e.g., -b \"174, 56, 5\"")


def usb(parser):
    parser.add_argument("-u", "--usb", dest="usb_camera", default=False, required=False, action="store_true",
                        help="Use USB Raspi camera [false]")


def flip_x(parser):
    parser.add_argument("-x", "--flipx", dest="flip_x", default=False, required=False, action="store_true",
                        help="Flip image on X axis[false]")


def flip_y(parser):
    parser.add_argument("-y", "--flipy", dest="flip_y", default=False, action="store_true",
                        help="Flip image on Y axis[false]")


def width(parser):
    parser.add_argument("-w", "--width", default=400, type=int, help="Image width [400]")


def middle_percent(parser):
    parser.add_argument("-e", "--percent", dest="middle_percent", default=15, type=int, help="Middle percent [15]")


def minimum_pixels(parser):
    parser.add_argument("-m", "--min", dest="minimum_pixels", default=100, type=int, help="Minimum pixel area [100]")


def hsv_range(parser):
    parser.add_argument("-r", "--range", dest="hsv_range", default=20, type=int, help="HSV range")


def grpc_port(parser):
    parser.add_argument("-p", "--port", dest="grpc_port", default=grpc_support.grpc_port_default, type=int,
                        help="gRPC port [{0}]".format(grpc_support.grpc_port_default))


def leds(parser):
    parser.add_argument("-l", "--leds", default=False, action="store_true",
                        help="Enable Blinkt led feedback [false]")


def display(parser):
    parser.add_argument("-d", "--display", default=False, action="store_true", help="Display image [false]")


def verbose(parser):
    parser.add_argument("-v", "--verbose", dest="loglevel", default=logging.INFO, action="store_const",
                        const=logging.DEBUG, help="Include debugging info", )


def grpc_host(parser):
    parser.add_argument("-g", "--grpc", dest="grpc_host", required=True, help="gRPC location server hostname")


def camera_name(parser):
    parser.add_argument("-c", "--camera", dest="camera_name", required=True, help="Camera name")


def camera_name_optional(parser):
    parser.add_argument("-c", "--camera", dest="camera_name", required=False, default="", help="Camera name")


def mqtt_host(parser):
    parser.add_argument("-m", "--mqtt", dest="mqtt_host", required=True, help="MQTT server hostname")


def calib(parser):
    parser.add_argument("-c", "--calib", default=False, type=bool, action="store_true", help="Calibration mode [false]")


def alternate(parser):
    parser.add_argument("-a", "--alternate", default=False, type=bool, action="store_true",
                        help="Alternate servo actions [false]")


def http_host(parser):
    parser.add_argument("-t", "--http", dest="http_host", default="localhost:8080", required=False,
                        help="HTTP hostname:port [localhost:8080]")


def http_delay_secs(parser):
    parser.add_argument("-s", "--delay", default=0.25, type=float, dest="http_delay_secs",
                        help="HTTP delay secs [0.25]")


def http_file(parser):
    parser.add_argument("-i", "--file", default=http_file_default, type=str, dest="http_file",
                        help="HTTP template file")
