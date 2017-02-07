import traceback
from logging import error
from logging import info
from threading import Event
from threading import Lock

from dict_utils import itervalues

grpc_port_default = 50051


class GenericClient(object):
    def __init__(self, hostname):
        self._hostname = hostname if ":" in hostname else hostname + ":{0}".format(grpc_port_default)
        self._lock = Lock()
        self._stopped = False


class GenericServer(object):
    def __init__(self, port):
        self._hostname = "[::]:" + str(port)
        self._grpc_server = None
        self._stopped = False
        self._cnt_lock = Lock()
        self._invoke_cnt = 0
        self._clients = {}
        self._lock = Lock()
        self._currval = None
        self._id = 0

    def set_currval(self, val):
        with self._lock:
            self._currval = val
            for v in itervalues(self._clients):
                v.set()

    def currval_generator(self, name):
        try:
            ready = Event()
            with self._lock:
                self._clients[name] = ready

            while not self._stopped:
                ready.wait()
                with self._lock:
                    if ready.is_set() and not self._stopped:
                        ready.clear()
                        val = self._currval
                        if val is not None:
                            yield val
                    else:
                        info("Skipped sending data to client {0}".format(name))
        except BaseException as e:
            error("Unknown error generating values [{0}]".format(e))
            traceback.print_exc()
        finally:
            info("Discontinued streaming values for client {0}".format(name))
            with self._lock:
                if self._clients.pop(name, None) is None:
                    error("Error releasing client {0}".format(name))

    def stop(self):
        if not self._stopped:
            info("Stopping server")
            self._stopped = True
            self.set_currval(None)
            self._grpc_server.stop(0)


class TimeoutException(Exception):
    def __init__(self, *args, **kwargs):
        pass
