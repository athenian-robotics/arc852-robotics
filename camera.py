import time

import cv2

from common_utils import is_raspi


class Camera(object):
    def __init__(self, src=0, use_picamera=True, resolution=(320, 240), framerate=32):
        if is_raspi():
            from imutils.video import VideoStream
            # Initialize the video stream
            self.__vs = VideoStream(src=src,
                                    usePiCamera=use_picamera,
                                    resolution=resolution,
                                    framerate=framerate).start()
            # Allow the cammera sensor to warmup
            time.sleep(2.0)
        else:
            self.__vc = cv2.VideoCapture(0)

    def is_open(self):
        return True if is_raspi() else self.__vc.isOpened()

    def read(self):
        return self.__vs.read() if is_raspi() else self.__vc.read()[1]

    def close(self):
        if is_raspi():
            self.__vs.stop()
        else:
            self.__vc.release()

        cv2.destroyAllWindows()
