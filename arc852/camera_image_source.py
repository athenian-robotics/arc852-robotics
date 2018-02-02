import time
from threading import Condition
from threading import Thread

import arc852.cli_args  as cli
from arc852.camera import Camera
from arc852.generic_image_source import GenericImageSource


class CameraImageSource(GenericImageSource):
    args = [cli.usb_camera, cli.usb_port]

    def __init__(self, usb_camera, usb_port):
        super(CameraImageSource, self).__init__()
        self.__cond = Condition()
        self.__cv2_img = None
        self.__cam = Camera(usb_camera=usb_camera, usb_port=usb_port)

    def start(self):
        Thread(target=self.__read_image).start()

    def stop(self):
        self.__cam.close()

    def __read_image(self):
        while self.__cam.is_open():
            self.__cond.acquire()

            self.__cv2_img = self.__cam.read()
            if self.__cv2_img is None:
                # logger.error("Null image read from camera")
                time.sleep(.5)
            else:
                self.__cond.notify()
            self.__cond.release()

    def get_image(self):
        self.__cond.acquire()
        while self.__cv2_img is None:
            self.__cond.wait()
        retval = self.__cv2_img
        self.__cv2_img = None
        self.__cond.release()
        return retval
