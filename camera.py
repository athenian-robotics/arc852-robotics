import time
from cv2 import VideoCapture, destroyAllWindows

from utils import is_raspi


class Camera(object):
    def __init__(self, src=0, usb_camera=False, usb_port=-1, resolution=(320, 240), framerate=32):
        self._usb_camera = usb_camera
        self._usb_port = usb_port

        if self.use_video_stream():
            from imutils.video import VideoStream
            # Initialize the video stream
            self.__vs = VideoStream(src=src,
                                    usePiCamera=usb_camera,
                                    resolution=resolution,
                                    framerate=framerate).start()
            # Allow the cammera sensor to warmup
            time.sleep(2.0)
        else:
            # On OSX, built-in camera use 0, usb cameras use 1 or greater
            if usb_port == -1:
                camera_num = 0 if is_raspi() or not self._usb_camera else 1
            else:
                camera_num = usb_port
            self.__vc = VideoCapture(camera_num)

    def use_video_stream(self):
        return not self._usb_camera and self._usb_port == -1 and is_raspi()

    def is_open(self):
        return True if self.use_video_stream() else self.__vc.isOpened()

    def read(self):
        return self.__vs.read() if self.use_video_stream() else self.__vc.read()[1]

    def close(self):
        if self.use_video_stream():
            self.__vs.stop()
        else:
            self.__vc.release()

        destroyAllWindows()
