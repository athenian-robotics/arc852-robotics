import time

from cv2 import VideoCapture, destroyAllWindows


class Camera(object):
    def __init__(self, src=0, use_picamera=True, resolution=(320, 240), framerate=32):
        self._use_picamera = use_picamera

        if self._use_picamera:
            from imutils.video import VideoStream
            # Initialize the video stream
            self.__vs = VideoStream(src=src,
                                    usePiCamera=use_picamera,
                                    resolution=resolution,
                                    framerate=framerate).start()
            # Allow the cammera sensor to warmup
            time.sleep(2.0)
        else:
            self.__vc = VideoCapture(0)
            self.__vc.set(15, -6)

    def is_open(self):
        return True if self._use_picamera else self.__vc.isOpened()

    def read(self):
        return self.__vs.read() if self._use_picamera else self.__vc.read()[1]

    def close(self):
        if self._use_picamera:
            self.__vs.stop()
        else:
            self.__vc.release()

        destroyAllWindows()
