import os
import sys

TOPIC = "topic"

__path = os.path.abspath(sys.modules[__name__].__file__)
__dirname = os.path.dirname(__path)
HTTP_TEMPLATE_DEFAULT = __dirname + "/html/single-image.html"
HTTP_PORT_DEFAULT = 8080
HTTP_HOST_DEFAULT = "localhost:{0}".format(HTTP_PORT_DEFAULT)
HTTP_DELAY_SECS_DEFAULT = 0.25

HTTP_PORT = "http_port"
TEMPLATE_FILE = "template_file"

MIDDLE_PERCENT_DEFAULT = 15
WIDTH_DEFAULT = 400
HSV_RANGE_DEFAULT = 20
MINIMUM_PIXELS_DEFAULT = 100
MAXIMUM_OBJECTS_DEFAULT = 10

DEFAULT_BAUD = 115200
OOR_SIZE_DEFAULT = 3
OOR_TIME_DEFAULT = 1000
OOR_UPPER_DEFAULT = -1

GRPC_PORT_DEFAULT = 50051
GRPC_HOST = "grpc_host"
GRPC_PORT = "grpc_port"
SERIAL_PORT = "serial_port"
BAUD_RATE = "baud_rate"
LED_NAME = "led_name"
LED_BRIGHTNESS = "led_brightness"
CAMERA_NAME = "camera_name"
CAMERA_NAME_DEFAULT = "Unnamed"
MQTT_HOST = "mqtt_host"
HTTP_HOST = "http_host"
HTTP_FILE = "http_file"
HTTP_DELAY_SECS = "http_delay_secs"
HTTP_VERBOSE = "http_verbose"
LOG_LEVEL = "loglevel"
LOG_FILE = "logfile"
MQTT_TOPIC = "mqtt_topic"
OOR_SIZE = "oor_size"
OOR_TIME = "oor_time"
OOR_UPPER = "oor_upper"
MINIMUM_PIXELS = "minimum_pixels"
MAXIMUM_OBJECTS = "maximum_objects"
LEDS = "leds"
DRAW_LINE = "draw_line"
DRAW_CONTOUR = "draw_contour"
DRAW_BOX = "draw_box"
HSV_RANGE = "hsv_range"
FILENAME = "filename"
FPS = "fps"
USB_CAMERA = "usb_camera"
USB_ID = "usb_id"
USB_PORT = "usb_port"
DISPLAY = "display"
BGR_COLOR = "bgr_color"
WIDTH = "width"
MIDDLE_PERCENT = "middle_percent"
IMAGE_TOPIC = "img_topic"
SO_TOPIC = "so_topic"
COMPRESSED = "compressed"
FORMAT = "format"
FLIP_X = "flip_x"
FLIP_Y = "flip_y"
MASK_X = "mask_x"
MASK_Y = "mask_y"
DEVICE_ID = "device_id"
VERTICAL_LINES = "vertical_lines"
HORIZONTAL_LINES = "horizontal_lines"

SERIAL_PORT_DEFAULT = "/dev/ttyACM0"
LED_BRIGHTNESS_DEFAULT = 0.10

#Ros Constants
ROS_PUBLISHER = "ros.publisher"
ROS_RATE = "ros.rate"
