import logging
import socket
import time
from threading import Thread

import paho.mqtt.client as paho


class MqttConnection(object):
    def __init__(self, hostname, port):
        self.__hostname = hostname
        self.__port = port
        self.__retry = True
        self.__client = paho.Client(userdata={"hostname": hostname, "port": port})
        self.__thread = None

    @property
    def client(self):
        return self.__client

    def connect(self):
        def connect_to_mqtt():
            while self.__retry:
                try:
                    logging.info("Connecting to MQTT broker {0}:{1}...".format(self.__hostname, self.__port))
                    self.__client.connect(self.__hostname, port=self.__port, keepalive=60)
                    self.__client.loop_forever()
                except socket.error:
                    logging.error("Cannot connect to MQTT broker {0}:{1}".format(self.__hostname, self.__port))
                    time.sleep(1)
                except BaseException as e:
                    logging.error("Cannot connect to MQTT broker {0}:{1} [e]".format(self.__hostname, self.__port, e))
                    time.sleep(1)

        if self.__thread is not None:
            logging.error("connect() already called")
        else:
            self.__thread = Thread(target=connect_to_mqtt, args=())
            self.__thread.start()

    def disconnect(self):
        self.__retry = False
        self.__client.disconnect()
