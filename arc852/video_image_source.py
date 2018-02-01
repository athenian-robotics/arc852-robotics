import logging
from threading import Condition
from threading import Thread

import cv2
import imutils
import rospy

import cli_args  as cli
from generic_image_source import GenericImageSource

logger = logging.getLogger(__name__)


class VideoImageSource(GenericImageSource):
    args = [cli.filename, cli.fps]

    def __init__(self, filename, fps_rate=30, width=600):
        super(VideoImageSource, self).__init__()
        self.__width = width
        self.__rate = rospy.Rate(fps_rate)
        self.__cond = Condition()
        self.__cv2_img = None
        self.__video = cv2.VideoCapture(filename)

    def start(self):
        Thread(target=self.__read_image).start()

    def stop(self):
        self.stopped = True

    def __read_image(self):
        while not self.stopped:
            self.__cond.acquire()
            try:
                ret, self.__cv2_img = self.__video.read()
                if not ret:
                    self.stopped = True
                    break
                else:
                    self.__cv2_img = imutils.resize(self.__cv2_img, width=self.__width)
            finally:
                self.__cond.notify()
                self.__cond.release()
            self.__rate.sleep()

    def get_image(self):
        self.__cond.acquire()
        while self.__cv2_img is None and not self.stopped:
            self.__cond.wait(timeout=1)
        retval = self.__cv2_img
        self.__cv2_img = None
        self.__cond.release()
        return retval
