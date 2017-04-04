import datetime
import logging
import math

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
    fname = file_name if file_name else "ct-{0}.png".format(datetime.datetime.now().strftime("%H-%M-%S"))
    cv2.imwrite(file_name, frame)
    if log_info:
        logger.info("Wrote image to %s", fname)


def encode_image(frame, ext=".jpg"):
    retval, buf = cv2.imencode(ext, frame)
    return retval, buf


def distance(point1, point2):
    xsqr = (point2[0] - point1[0]) ** 2
    ysqr = (point2[1] - point1[1]) ** 2
    return int(math.sqrt(xsqr + ysqr))


def contour_slope_degrees(contour):
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)

    # if self.__display:
    #    cv2.drawContours(image, [np.int0(box)], 0, RED, 2)

    point_lr = box[0]
    point_ll = box[1]
    point_ul = box[2]
    point_ur = box[3]

    line1 = distance(point_lr, point_ur)
    line2 = distance(point_ur, point_ul)

    if line1 < line2:
        point_lr = box[1]
        point_ll = box[2]
        point_ul = box[3]
        point_ur = box[0]
        line_width = line1
    else:
        line_width = line2

    delta_y = point_lr[1] - point_ur[1]
    delta_x = point_lr[0] - point_ur[0]

    # Calculate angle of line
    if delta_x == 0:
        # Vertical line
        slope = None
        degrees = 90
    else:
        # Non-vertical line
        slope = delta_y / delta_x
        radians = math.atan(slope)
        degrees = int(math.degrees(radians)) * -1

    return slope, degrees
