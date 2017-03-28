import logging
import time
from threading import Event
from threading import Lock
from threading import Thread

from constants import GRPC_PORT_DEFAULT
from utils import current_time_millis
from utils import itervalues, add_http_prefix

logger = logging.getLogger(__name__)


def grpc_url(hostname):
    return hostname if ":" in hostname else hostname + ":{0}".format(GRPC_PORT_DEFAULT)


class GenericClient(object):
    def __init__(self, hostname, http_hostname=False, desc=None):
        self.__desc = desc if desc else "client"
        self.__hostname = grpc_url(hostname) if not http_hostname else add_http_prefix(hostname)
        self.__started = False
        self.__stopped = False
        self.__value_lock = Lock()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    @property
    def hostname(self):
        return self.__hostname

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
        if not self.__started:
            logger.info("Starting {0}".format(self.desc))
            Thread(target=self._get_values).start()
            self.__started = True
        else:
            logger.error("{0} already started".format(self.desc))
        return self

    def stop(self):
        if not self.stopped:
            logger.info("Stopping {0}".format(self.desc))
            self.stopped = True
            self._mark_ready()
        return self


class SingleValueClient(GenericClient):
    def __init__(self, hostname, http_hostname=False, desc=None):
        super(SingleValueClient, self).__init__(hostname=hostname, desc=desc, http_hostname=http_hostname)
        self.__ready = Event()
        self.__currval = None

    @property
    def currval(self):
        return self.__currval

    @currval.setter
    def currval(self, val):
        self.__currval = val

    def _mark_ready(self):
        self.__ready.set()

    # Blocking
    def value(self, timeout=None):
        while not self.stopped:
            if not self.__ready.wait(timeout):
                raise TimeoutException
            with self.value_lock:
                if self.__ready.is_set() and not self.stopped:
                    self.__ready.clear()
                    return self.currval

    def values(self):
        while not self.stopped:
            yield self.value()


class GenericServer(object):
    def __init__(self, port=None, desc=None):
        self.__desc = desc if desc else "server"
        # self.__hostname = "localhost:{0}".format(port if port else GRPC_PORT_DEFAULT)
        self.__hostname = "[::]:{0}".format(port if port else GRPC_PORT_DEFAULT)
        self.__started = False
        self.__stopped = False
        self.__clients_lock = Lock()
        self.__cnt_lock = Lock()
        self.__invoke_cnt = 0
        self.__clients = {}
        self.__grpc_server = None
        self.__currval = None
        self.__id = 0
        self.__currval_cnt = 0

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return self

    @property
    def hostname(self):
        return self.__hostname

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
    def id(self):
        return self.__id

    @id.setter
    def id(self, val):
        self.__id = val

    @property
    def grpc_server(self):
        return self.__grpc_server

    @grpc_server.setter
    def grpc_server(self, val):
        self.__grpc_server = val

    def _init_values_on_start(self):
        raise NotImplementedError('Method not implemented!')

    def _start_server(self):
        raise NotImplementedError('Method not implemented!')

    def start(self):
        if not self.__started:
            logger.info("Starting {0}".format(self.desc))
            self._init_values_on_start()
            Thread(target=self._start_server).start()
            self.__started = True
            time.sleep(1)
        else:
            logger.error("{0} already started".format(self.desc))
        return self

    def stop(self):
        if not self.stopped:
            logger.info("Stopping {0}".format(self.desc))
            self.stopped = True
            self.set_currval(None)
            self.grpc_server.stop(0)
        return self

    def increment_cnt(self):
        with self.__cnt_lock:
            self.__invoke_cnt += 1
        return self.__invoke_cnt

    def set_currval(self, val):
        with self.__clients_lock:
            self.__currval = val
            for v in itervalues(self.__clients):
                v.set()

    def get_currval(self):
        with self.__clients_lock:
            return self.__currval

    # This is overridden by sub-class if adjustment necessary
    def _adjust_currval(self, currval, start_time):
        return currval

    def currval_generator(self, client_id):
        ready = Event()

        with self.__clients_lock:
            start_time = current_time_millis()
            self.__currval_cnt += 1
            unique_id = "{0}/{1}".format(client_id, self.__currval_cnt)
            self.__clients[unique_id] = ready

        client_desc = "{0} client {1}".format(self.desc, unique_id)

        logger.info("Starting to stream values for {0}".format(client_desc))

        try:
            while not self.stopped:
                ready.wait()
                with self.__clients_lock:
                    if ready.is_set() and not self.stopped:
                        ready.clear()
                        val = self._adjust_currval(self.__currval, start_time)
                        if val:
                            yield val
                    else:
                        logger.info("Skipped sending data to {0}".format(client_desc))
        except GeneratorExit:
            logger.info("Disconnected {0}".format(client_desc))
        except BaseException as e:
            logger.error("Unknown error generating values [{0}]".format(e), exc_info=True)
        finally:
            logger.info("Discontinued streaming values for {0}".format(client_desc))
            with self.__clients_lock:
                if self.__clients.pop(unique_id, None) is None:
                    logger.error("Error releasing {0}".format(client_desc))


class CannotConnectException(Exception):
    def __init__(self, hostname, *args, **kwargs):
        self.__hostname = hostname

    def __str__(self):
        return "Cannot connect to server at {0}".format(self.__hostname)


class TimeoutException(Exception):
    def __init__(self, *args, **kwargs):
        pass
