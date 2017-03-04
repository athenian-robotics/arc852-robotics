import logging
import time
from threading import Event
from threading import Lock
from threading import Thread

from constants import GRPC_PORT_DEFAULT
from utils import itervalues

logger = logging.getLogger(__name__)


class GenericClient(object):
    def __init__(self, hostname, desc):
        self.__desc = desc
        self._hostname = hostname if ":" in hostname else hostname + ":{0}".format(GRPC_PORT_DEFAULT)
        self.__stopped = False
        self.__value_lock = Lock()

    @property
    def desc(self):
        return self.__desc

    @property
    def value_lock(self):
        return self.__value_lock

    @property
    def stopped(self):
        return self.__stopped

    @stopped.setter
    def stopped(self, val):
        self.__stopped = val

    def _mark_ready(self):
        raise NotImplementedError('Method not implemented!')

    def _get_values(self, pause_secs=2.0):
        raise NotImplementedError('Method not implemented!')

    def start(self):
        logger.info("Starting {0}".format(self.desc))
        Thread(target=self._get_values).start()
        return self

    def stop(self):
        if not self.stopped:
            logger.info("Stopping {0}".format(self.desc))
            self.stopped = True
            self._mark_ready()


class GenericServer(object):
    def __init__(self, port, desc):
        self.__desc = desc
        self._hostname = "[::]:" + str(port)
        self.__stopped = False
        self.__clients_lock = Lock()
        self.__cnt_lock = Lock()
        self._invoke_cnt = 0
        self._clients = {}
        self._grpc_server = None
        self._currval = None
        self._id = 0

    @property
    def desc(self):
        return self.__desc

    @property
    def stopped(self):
        return self.__stopped

    @property
    def cnt_lock(self):
        return self.__cnt_lock

    @stopped.setter
    def stopped(self, val):
        self.__stopped = val

    def set_currval(self, val):
        with self.__clients_lock:
            self._currval = val
            for v in itervalues(self._clients):
                v.set()

    def currval_generator(self, name):
        client_desc = "{0} client {1}".format(self.desc, name)
        try:
            ready = Event()
            with self.__clients_lock:
                self._clients[name] = ready

            while not self.stopped:
                ready.wait()
                with self.__clients_lock:
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
            with self.__clients_lock:
                if self._clients.pop(name, None) is None:
                    logger.error("Error releasing {0}".format(client_desc))

    def _init_values_on_start(self):
        raise NotImplementedError('Method not implemented!')

    def _start_server(self):
        raise NotImplementedError('Method not implemented!')

    def start(self):
        logger.info("Starting {0}".format(self.desc))
        self._init_values_on_start()
        Thread(target=self._start_server).start()
        time.sleep(1)
        return self

    def stop(self):
        if not self.stopped:
            logger.info("Stopping {0}".format(self.desc))
            self.stopped = True
            self.set_currval(None)
            self._grpc_server.stop(0)


class TimeoutException(Exception):
    def __init__(self, *args, **kwargs):
        pass
