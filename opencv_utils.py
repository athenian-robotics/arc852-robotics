import datetime
import logging

import cv2

RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)

logger = logging.getLogger(__name__)

def get_moment(contour):
    moment1 = cv2.moments(contour)
    area = int(moment1["m00"])
    x = int(moment1["m10"] / area)
    y = int(moment1["m01"] / area)
    return contour, area, x, y


def write_image(frame, file_name=None, log_info=False):
    fname = file_name if file_name is not None else "ct-{0}.png".format(datetime.datetime.now().strftime("%H-%M-%S"))
    cv2.imwrite(file_name, frame)
    if log_info:
        logger.info("Wrote image to {0}".format(fname))


def encode_image(frame, ext=".jpg"):
    retval, buf = cv2.imencode(ext, frame)
    return retval, buf


def get_list_arg(val):
    return eval(val if "[" in val else "[{0}]".format(val))
