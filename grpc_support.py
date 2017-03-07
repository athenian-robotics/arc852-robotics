import logging
import time
from threading import Event
from threading import Lock
from threading import Thread

from constants import GRPC_PORT_DEFAULT
from utils import itervalues

logger = logging.getLogger(__name__)


class GenericClient(object):
    def __init__(self, hostname, desc=None):
        self.__desc = desc if desc else "client"
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
    def __init__(self, port=None, desc=None):
        self.__desc = desc if desc else "server"
        self._hostname = "[::]:{0}".format(port if port else GRPC_PORT_DEFAULT)
        self.__stopped = False
        self.__clients_lock = Lock()
        self.__cnt_lock = Lock()
        self.__invoke_cnt = 0
        self._clients = {}
        self._grpc_server = None
        self._currval = None
        self._id = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @property
    def desc(self):
        return self.__desc

    @property
    def stopped(self):
        return self.__stopped

    @stopped.setter
    def stopped(self, val):
        self.__stopped = val

    @property
    def grpc_server(self):
        return self._grpc_server

    @grpc_server.setter
    def grpc_server(self, val):
        self._grpc_server = val

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
            self.grpc_server.stop(0)

    def increment_cnt(self):
        with self.__cnt_lock:
            self.__invoke_cnt += 1
        return self.__invoke_cnt

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
                        if val:
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


class CannotConnectException(Exception):
    def __init__(self, hostname, *args, **kwargs):
        self._hostname = hostname

    def __str__(self):
        return "Cannot connect to server at {0}".format(self._hostname)


class TimeoutException(Exception):
    def __init__(self, *args, **kwargs):
        pass
