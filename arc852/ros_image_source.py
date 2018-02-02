from threading import Condition

import rospy
from cv_bridge import CvBridge
from sensor_msgs.msg import CompressedImage, Image

import arc852.cli_args  as cli
from arc852.generic_image_source import GenericImageSource


class RosImageSource(GenericImageSource):
    args = [cli.image_topic, cli.compressed, cli.format]

    def __init__(self, topic, compressed, format):
        super(RosImageSource, self).__init__()
        self.__topic = topic
        self.__compressed = compressed
        self.__format = format

        self.__cond = Condition()
        self.__cv2_img = None
        self.__bridge = CvBridge()

    def start(self):
        rospy.Subscriber(self.__topic,
                         CompressedImage if self.__compressed else Image,
                         self.__image_cb)

    def stop(self):
        self.stopped = True

    def __image_cb(self, msg):
        self.__cond.acquire()
        if self.__compressed:
            self.__cv2_img = self.__bridge.compressed_imgmsg_to_cv2(msg, self.__format)
        else:
            self.__cv2_img = self.__bridge.imgmsg_to_cv2(msg, self.__format)
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
