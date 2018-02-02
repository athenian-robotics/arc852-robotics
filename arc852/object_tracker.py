import logging
import time

import cv2
import imutils
import numpy as np

import arc852.cli_args  as cli
import arc852.opencv_utils as utils

logger = logging.getLogger(__name__)

BLACK = np.uint8((0, 0, 0))


class ObjectTracker(object):
    args = [cli.width, cli.middle_percent, cli.display, cli.flip_x, cli.flip_y, cli.mask_x, cli.mask_y]

    def __init__(self, image_source, image_server, width, middle_percent, display, flip_x, flip_y, mask_x, mask_y):
        self.__image_source = image_source
        self.__image_server = image_server
        self.__width = width
        self.__middle_percent = middle_percent
        self.__orig_width = width
        self.__orig_middle_percent = middle_percent
        self.__display = display
        self.__flip_x = flip_x
        self.__flip_y = flip_y
        self.__mask_x = mask_x
        self.__mask_y = mask_y
        self.__filters = None

        self.__image = None
        self.__stopped = False
        self.cnt = 0

    @property
    def width(self):
        return self.__width

    @width.setter
    def width(self, width):
        if 200 <= width <= 4000:
            self.__width = width
            if self.__filters:
                for f in self.__filters:
                    f.reset()

    @property
    def middle_percent(self):
        return self.__middle_percent

    @middle_percent.setter
    def middle_percent(self, val):
        if 2 <= val <= 98:
            self.__middle_percent = val
            if self.__filters:
                for filter in self.__filters:
                    filter.reset()

    @property
    def markup_image(self):
        return self.__display or (self.__image_server is not None and self.__image_server.enabled)

    def __read_image(self):
        try:
            cv2_img = self.__image_source.get_image()

            if cv2_img is None:
                return None

            cv2_img = imutils.resize(cv2_img, width=self.width)

            if self.__flip_x:
                cv2_img = cv2.flip(cv2_img, 0)

            if self.__flip_y:
                cv2_img = cv2.flip(cv2_img, 1)

            # Apply masks
            if self.__mask_y != 0:
                height, width = cv2_img.shape[:2]
                mask_height = abs(int((self.__mask_y / 100.0) * height))
                if self.__mask_y < 0:
                    cv2_img[0: mask_height, 0: width] = BLACK
                else:
                    cv2_img[height - mask_height: height, 0: width] = BLACK

            if self.__mask_x != 0:
                height, width = cv2_img.shape[:2]
                mask_width = abs(int((self.__mask_x / 100.0) * width))
                if self.__mask_x < 0:
                    cv2_img[0: height, 0: mask_width] = BLACK
                else:
                    cv2_img[0: height, width - mask_width: width] = BLACK

            if self.__filters:
                for f in self.__filters:
                    f.process_image(cv2_img)
                for f in self.__filters:
                    if f.predicate:
                        f.predicate(f)
                    f.publish_data()
                    f.markup_image(cv2_img)

            self.cnt += 1

            return cv2_img

        except KeyboardInterrupt as e:
            raise e
        except BaseException as e:
            logger.error("Unexpected error in main loop [{0}]".format(e), exc_info=True)
            time.sleep(1)

    # Do not run this in a background thread. cv2.waitKey has to run in main thread
    def run(self, *filters):
        self.__filters = filters

        if self.__filters:
            for f in self.__filters:
                f.start()

        while not self.__stopped and not self.__image_source.stopped:
            img = self.__read_image()
            if img is not None:
                if self.__image_server is not None:
                    self.__image_server.image = img

                if self.__display:
                    self.display_image(img)
            else:
                time.sleep(0.1)

    def cleanup(self):
        if self.__filters:
            for f in self.__filters:
                f.stop()

    def display_image(self, image):
        cv2.imshow("Image", image)

        key = cv2.waitKey(1) & 0xFF

        if key == 255:
            pass
        elif key == ord("w"):
            self.width -= 10
        elif key == ord("W"):
            self.width += 10
        elif key == ord("-") or key == ord("_") or key == 0:
            self.middle_percent -= 1
        elif key == ord("+") or key == ord("=") or key == 1:
            self.middle_percent += 1
        elif key == ord("r"):
            self.width = self.__orig_width
            self.middle_percent = self.__orig_middle_percent
        elif key == ord("s"):
            utils.write_image(image, log_info=True)
        elif key == ord("q"):
            self.__stopped = True
