import socket
import time
import traceback
from logging import error
from logging import info
from threading import Thread

import paho.mqtt.client as paho


class MqttConnection(object):
    def __init__(self, hostname, port, userdata=None):
        self.__hostname = hostname
        self.__port = port
        self.__retry = True
        self.__client = paho.Client(userdata=userdata)
        self.__thread = None

    @property
    def client(self):
        return self.__client

    def connect(self):
        def connect_to_mqtt():
            while self.__retry:
                try:
                    info("Connecting to MQTT broker {0}:{1}...".format(self.__hostname, self.__port))
                    self.__client.connect(self.__hostname, port=self.__port, keepalive=60)
                    self.__client.loop_forever()
                except socket.error:
                    error("Cannot connect to MQTT broker {0}:{1}".format(self.__hostname, self.__port))
                    time.sleep(1)
                except BaseException as e:
                    error("Cannot connect to MQTT broker {0}:{1} [{2}]".format(self.__hostname, self.__port, e))
                    traceback.print_exc()
                    time.sleep(1)

        if self.__thread is not None:
            error("connect() already called")
        else:
            self.__thread = Thread(target=connect_to_mqtt)
            self.__thread.start()

    def disconnect(self):
        self.__retry = False
        self.__client.disconnect()
