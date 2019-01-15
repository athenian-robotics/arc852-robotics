import logging
import time

import cv2
import imutils
import numpy as np

import arc852.cli_args  as cli
import arc852.opencv_defaults as defs
from arc852.opencv_utils import GREEN
from arc852.opencv_utils import RED

logger = logging.getLogger(__name__)


class ColorPicker(object):
    args = [cli.width, cli.flip_x, cli.flip_y]

    roi_size = 24
    orig_roi_size = roi_size
    roi_inc = 6
    move_inc = 4
    x_adj = 0
    y_adj = 0

    def __init__(self, image_source, width, flip_x, flip_y):
        self.__image_source = image_source
        self.__width = width
        self.__flip_x = flip_x
        self.__flip_y = flip_y
        self.__orig_width = self.__width
        self.__roi_x = 0
        self.__roi_y = 0
        self.__bgr_text = ""
        self.__img_width = 0
        self.__img_height = 0
        self.__stopped = False
        self.__cnt = 0

    @property
    def cnt(self):
        return self.__cnt

    def __read_image(self):
        try:
            cv2_img = self.__image_source.get_image()

            cv2_img = imutils.resize(cv2_img, width=self.__width)

            if self.__flip_x:
                cv2_img = cv2.flip(cv2_img, 0)

            if self.__flip_y:
                cv2_img = cv2.flip(cv2_img, 1)

            self.__img_height, self.__img_width = cv2_img.shape[:2]

            self.__roi_x = int((self.__img_width / 2) - (self.roi_size / 2) + self.x_adj)
            self.__roi_y = int((self.__img_height / 2) - (self.roi_size / 2) + self.y_adj)
            roi = cv2_img[self.__roi_y:self.__roi_y + self.roi_size, self.__roi_x:self.__roi_x + self.roi_size]

            roi_h, roi_w = roi.shape[:2]
            roi_canvas = np.zeros((roi_h, roi_w, 3), dtype="uint8")
            roi_canvas[0:roi_h, 0:roi_w] = roi

            # Calculate averge color in ROI
            avg_color_per_row = np.average(roi_canvas, axis=0)
            avg_color = np.average(avg_color_per_row, axis=0)
            avg_color = np.uint8(avg_color)

            # Draw a rectangle around the sample area
            cv2.rectangle(cv2_img, (self.__roi_x, self.__roi_y),
                          (self.__roi_x + self.roi_size, self.__roi_y + self.roi_size),
                          GREEN, 1)

            # Add text info
            self.__bgr_text = "#{0} BGR value: [{1}, {2}, {3}]".format(self.cnt, avg_color[0], avg_color[1],
                                                                       avg_color[2])
            roi_text = " ROI: {0}x{1} ".format(str(self.roi_size), str(self.roi_size))
            cv2.putText(cv2_img, self.__bgr_text + roi_text, defs.TEXT_LOC, defs.TEXT_FONT, defs.TEXT_SIZE, RED, 1)

            # Overlay color swatch on image
            size = int(self.__img_width * 0.20)
            cv2_img[self.__img_height - size:self.__img_height, self.__img_width - size:self.__img_width] = avg_color

            if self.cnt % 30 == 0:
                logger.info(self.__bgr_text)

            self.__cnt += 1
            return cv2_img

        except BaseException as e:
            logger.error("Unexpected error in main loop [{0}]".format(e), exc_info=True)
            time.sleep(1)

    # Do not run this in a background thread because cv2.waitKey has to run in main thread
    def run(self):
        while not self.__stopped:
            img = self.__read_image()
            if img is not None:
                self.display_image(img)
            else:
                logger.info("No image")
                time.sleep(1)

    def display_image(self, image):
        # Display image
        cv2.imshow("Image", image)

        # print("Start wait 1")
        key = cv2.waitKey(1) & 0xFF
        # print("End wait 1")

        if key == 255:
            pass
        elif key == ord("c") or key == ord(" "):
            print(self.__bgr_text)
        elif self.__roi_y >= self.move_inc and (key == 0 or key == ord("k")):  # Up
            self.y_adj -= self.move_inc
        elif self.__roi_y <= self.__img_height - self.roi_size - self.move_inc and (
                key == 1 or key == ord("j")):  # Down
            self.y_adj += self.move_inc
        elif self.__roi_x >= self.move_inc and (key == 2 or key == ord("h")):  # Left
            self.x_adj -= self.move_inc
        elif self.__roi_x <= self.__img_width - self.roi_size - self.move_inc - self.move_inc \
                and (key == 3 or key == ord("l")):  # Right
            self.x_adj += self.move_inc
        elif self.roi_size >= self.roi_inc * 2 and (key == ord("-") or key == ord("_")):
            self.roi_size -= self.roi_inc
            self.x_adj, self.y_adj = 0, 0
        elif self.roi_size <= self.roi_inc * 49 and (key == ord("+") or key == ord("=")):
            self.roi_size += self.roi_inc
            self.x_adj, self.y_adj = 0, 0
        elif key == ord("r"):
            self.__width = self.__orig_width
            self.roi_size = self.orig_roi_size
        elif key == ord("<"):
            self.__width -= 10
        elif key == ord(">"):
            self.__width += 10
        elif key == ord("q"):
            self.__stopped = True
