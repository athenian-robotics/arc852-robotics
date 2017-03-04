import logging
from threading import Event
from threading import Lock

from constants import GRPC_PORT_DEFAULT
from utils import itervalues

logger = logging.getLogger(__name__)


class GenericClient(object):
    def __init__(self, hostname):
        self._hostname = hostname if ":" in hostname else hostname + ":{0}".format(GRPC_PORT_DEFAULT)
        self.__stopped = False
        self._lock = Lock()

    @property
    def stopped(self):
        return self.__stopped

    @stopped.setter
    def stopped(self, val):
        self.__stopped = val


class GenericServer(object):
    def __init__(self, port, desc):
        self.__desc = desc
        self._hostname = "[::]:" + str(port)
        self.__stopped = False
        self._lock = Lock()
        self._cnt_lock = Lock()
        self._invoke_cnt = 0
        self._clients = {}
        self._grpc_server = None
        self._currval = None
        self._id = 0

    @property
    def stopped(self):
        return self.__stopped

    @stopped.setter
    def stopped(self, val):
        self.__stopped = val

    @property
    def desc(self):
        return self.__desc

    def set_currval(self, val):
        with self._lock:
            self._currval = val
            for v in itervalues(self._clients):
                v.set()

    def currval_generator(self, name):
        client_desc = "{0} client {1}".format(self.desc, name)
        try:
            ready = Event()
            with self._lock:
                self._clients[name] = ready

            while not self.stopped:
                ready.wait()
                with self._lock:
                    if ready.is_set() and not self.stopped:
                        ready.clear()
                        val = self._currval
                        if val is not None:
                            yield val
                    else:
                        logger.info("Skipped sending data to {0}".format(client_desc))
        except GeneratorExit:
            logger.info("gRPC {0} disconnected".format(client_desc))
        except BaseException as e:
            logger.error("Unknown error generating values [{0}]".format(e), exc_info=True)
        finally:
            logger.info("Discontinued streaming values for {0}".format(client_desc))
            with self._lock:
                if self._clients.pop(name, None) is None:
                    logger.error("Error releasing {0}".format(client_desc))

    def stop(self):
        if not self.stopped:
            logger.info("Stopping {0}".format(self.desc))
            self.stopped = True
            self.set_currval(None)
            self._grpc_server.stop(0)


class TimeoutException(Exception):
    def __init__(self, *args, **kwargs):
        pass
