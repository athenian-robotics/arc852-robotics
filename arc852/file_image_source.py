import cv2

import arc852.cli_args  as cli
from arc852.generic_image_source import GenericImageSource


class FileImageSource(GenericImageSource):
    args = [cli.filename]

    def __init__(self, filename):
        super(FileImageSource, self).__init__()
        self.__cv2_img = cv2.imread(filename)

    def start(self):
        pass

    def stop(self):
        pass

    def get_image(self):
        return self.__cv2_img
