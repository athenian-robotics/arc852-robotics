import os
import sys

TOPIC = "topic"

__path = os.path.abspath(sys.modules[__name__].__file__)
__dirname = os.path.dirname(__path)
HTTP_TEMPLATE_DEFAULT = __dirname + "/html/image-reader.html"
HTTP_PORT_DEFAULT = 8080
HTTP_HOST_DEFAULT = "localhost:{0}".format(HTTP_PORT_DEFAULT)
HTTP_DELAY_SECS_DEFAULT = 0.25

MIDDLE_PERCENT_DEFAULT = 15
WIDTH_DEFAULT = 400
HSV_RANGE_DEFAULT = 20
MINIMUM_PIXELS_DEFAULT = 100

DEFAULT_BAUD = 115200

GRPC_PORT_DEFAULT = 50051
GRPC_HOST = "grpc_host"
GRPC_PORT = "grpc_port"
SERIAL_PORT = "serial_port"
BAUD_RATE = "baud_rate"
CAMERA_NAME = "camera_name"
CAMERA_NAME_DEFAULT = "Unnamed"
MQTT_HOST = "mqtt_host"
HTTP_HOST = "http_host"
HTTP_DELAY_SECS = "http_delay_secs"
HTTP_FILE = "http_file"
LOG_LEVEL = "loglevel"
MINIMUM_PIXELS = "minimum_pixels"
LEDS = "leds"
HSV_RANGE = "hsv_range"
USB_CAMERA = "usb_camera"
DISPLAY = "display"
BGR_COLOR = "bgr_color"
WIDTH = "width"
MIDDLE_PERCENT = "middle_percent"
FLIP_X = "flip_x"
FLIP_Y = "flip_y"

SERIAL_PORT_DEFAULT = "/dev/ttyACM0"
