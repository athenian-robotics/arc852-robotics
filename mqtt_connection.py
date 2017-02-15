import logging
import socket
import time
from threading import Thread

import paho.mqtt.client as paho
from utils import mqtt_broker_info

logger = logging.getLogger(__name__)

class MqttConnection(object):
    def __init__(self,
                 hostname,
                 userdata={},
                 on_connect=None,
                 on_disconnect=None,
                 on_publish=None,
                 on_subscribe=None,
                 on_message=None,
                 on_message_filtered=None,
                 on_log=None):
        self.__hostname, self.__port = mqtt_broker_info(hostname)

        self.__retry = True
        self.__thread = None

        # Create Paho client
        self.client = paho.Client(userdata=userdata)

        if userdata:
            userdata["paho.client"] = self.client
            if not userdata.get("paho.hostname"):
                userdata["paho.hostname"] = self.__hostname
            if not userdata.get("paho.port"):
                userdata["paho.port"] = self.__port

        if on_connect:
            self.client.on_connect = on_connect
        if on_disconnect:
            self.client.on_disconnect = on_disconnect
        if on_subscribe:
            self.client.on_subscribe = on_subscribe
        if on_publish:
            self.client.on_publish = on_publish
        if on_message:
            self.client.on_message = on_message
        if on_message_filtered:
            self.client.on_message_filtered = on_message_filtered
        if on_log:
            self.client.on_log = on_log

    def connect(self):
        def connect_to_mqtt():
            while self.__retry:
                try:
                    logger.info("Connecting to MQTT broker {0}:{1}...".format(self.__hostname, self.__port))
                    self.client.connect(self.__hostname, port=self.__port, keepalive=60)
                    self.client.loop_forever()
                except socket.error:
                    logger.error("Cannot connect to MQTT broker {0}:{1}".format(self.__hostname, self.__port))
                    time.sleep(1)
                except BaseException as e:
                    logger.error("Cannot connect to MQTT broker {0}:{1} [{2}]".format(self.__hostname, self.__port, e),
                                 exc_info=True)
                    time.sleep(1)

        if self.__thread is not None:
            logger.error("MqttConnection.connect() already called")
        else:
            self.__thread = Thread(target=connect_to_mqtt)
            self.__thread.start()
        return self

    def disconnect(self):
        self.__retry = False
        self.client.disconnect()
