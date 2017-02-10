import argparse
import logging

from grpc_support import GRPC_PORT_DEFAULT
from image_server import HTTP_DELAY_SECS_DEFAULT, HTTP_HOST_DEFAULT, HTTP_TEMPLATE_DEFAULT, CAMERA_NAME_DEFAULT


def setup_cli_args(*args):
    parser = argparse.ArgumentParser()
    for arg in args:
        arg(parser)
    return vars(parser.parse_args())


bgr = lambda p: p.add_argument("-b", "--bgr", dest="bgr_color", required=True, type=str,
                               help="BGR target value, e.g., -b \"174, 56, 5\"")

usb = lambda p: p.add_argument("-u", "--usb", dest="usb_camera", default=False, required=False, action="store_true",
                               help="Use USB Raspi camera [false]")

flip_x = lambda p: p.add_argument("-x", "--flipx", dest="flip_x", default=False, required=False, action="store_true",
                                  help="Flip image on X axis[false]")

flip_y = lambda p: p.add_argument("-y", "--flipy", dest="flip_y", default=False, action="store_true",
                                  help="Flip image on Y axis[false]")

width = lambda p: p.add_argument("-w", "--width", default=400, type=int, help="Image width [400]")

middle_percent = lambda p: p.add_argument("-e", "--percent", dest="middle_percent", default=15, type=int,
                                          help="Middle percent [15]")

minimum_pixels = lambda p: p.add_argument("-m", "--min", dest="minimum_pixels", default=100, type=int,
                                          help="Minimum pixel area [100]")

hsv_range = lambda p: p.add_argument("-r", "--range", dest="hsv_range", default=20, type=int, help="HSV range")

grpc_port = lambda p: p.add_argument("-p", "--port", dest="grpc_port", default=GRPC_PORT_DEFAULT, type=int,
                                     help="gRPC port [{0}]".format(GRPC_PORT_DEFAULT))

leds = lambda p: p.add_argument("-l", "--leds", default=False, action="store_true",
                                help="Enable Blinkt led feedback [false]")

display = lambda p: p.add_argument("-d", "--display", default=False, action="store_true", help="Display image [false]")

grpc_host = lambda p: p.add_argument("-g", "--grpc", dest="grpc_host", required=True,
                                     help="gRPC location server hostname")

camera_name = lambda p: p.add_argument("-c", "--camera", dest="camera_name", required=True, help="Camera name")

camera_name_optional = lambda p: p.add_argument("-c", "--camera", dest="camera_name", required=False,
                                                default=CAMERA_NAME_DEFAULT, help="Camera name")

mqtt_host = lambda p: p.add_argument("-m", "--mqtt", dest="mqtt_host", required=True, help="MQTT server hostname")

calib = lambda p: p.add_argument("-c", "--calib", default=False, action="store_true", help="Calibration mode [false]")

alternate = lambda p: p.add_argument("-a", "--alternate", default=False, action="store_true",
                                     help="Alternate servo actions [false]")

http_host = lambda p: p.add_argument("-t", "--http", dest="http_host", default=HTTP_HOST_DEFAULT, required=False,
                                     help="HTTP hostname:port [{0}]".format(HTTP_HOST_DEFAULT))

http_delay_secs = lambda p: p.add_argument("-s", "--delay", default=HTTP_DELAY_SECS_DEFAULT, type=float,
                                           dest="http_delay_secs",
                                           help="HTTP delay secs [{0}]".format(HTTP_DELAY_SECS_DEFAULT))

http_file = lambda p: p.add_argument("-i", "--file", default=HTTP_TEMPLATE_DEFAULT, type=str,
                                     dest="http_file", help="HTTP template file")

verbose_http = lambda p: p.add_argument("-o", "--verbose-http", default=False, action="store_true", dest="http_verbose",
                                        help="Enable verbose HTTP log [false]")

verbose = lambda p: p.add_argument("-v", "--verbose", dest="loglevel", default=logging.INFO, action="store_const",
                                   const=logging.DEBUG, help="Enable\ debugging info", )
