import logging
import sys
import time
from threading import Event
from threading import Lock
from threading import Thread

import serial
import serial.tools.list_ports
from prometheus_client import Histogram

from arc852.constants import DEFAULT_BAUD
from arc852.utils import is_windows

logger = logging.getLogger(__name__)

DEVICE = "Device"
MANF = "Manufacturer"
HWID = "HWID"
SN = "SN"

# Create a metric to track time spent and requests made.
READ_TIME = Histogram('serial_read_seconds', 'Time spent reading serial data')
PROCESS_TIME = Histogram('serial_processing_seconds', 'Time spent processing serial data')

class SerialReader(object):
    def __init__(self,
                 func,
                 userdata=None,
                 port="/dev/ttyACM0",
                 baudrate=DEFAULT_BAUD,
                 debug=False,
                 log_info=logger.info,
                 log_debug=logger.debug,
                 log_error=logger.error,):
        self.__func = func
        self.__userdata = userdata
        self.__baudrate = baudrate
        self.__port_path = ("" if (is_windows() or "/dev/" in str(port)) else "/dev/") + str(port)
        self.__lock = Lock()
        self.__event = Event()
        self.__stopped = False
        self.__data = None
        self.__log_info = log_info
        self.__log_debug = log_debug
        self.__log_error = log_error

        self.__log_info("Serial port info:")
        for i in SerialReader.all_ports():
            self.__log_info(i)


    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return self

    # Read data from serial port and pass it along to the consumer
    # If the consumer runs slower than the producer, then values will be dropped
    def read_serial_data(self, port, baudrate):
        ser = None
        try:
            # Open serial port
            ser = serial.Serial(port=port, baudrate=baudrate)
            self.__log_info("Reading data from serial port {} at {}".format(port, baudrate))

            while not self.__stopped:
                with READ_TIME.time():
                    b = None
                    try:
                        # Read data from serial port.  Ignore the trailing two chars with [:-2]
                        # Do not call readline() inside mutex because it might block
                        b = ser.readline()[:-2]
                        #print("We got DATA!!!")
                        # Update data with mutex
                        with self.__lock:
                            self.__data = b.decode("utf-8")

                        # Notify consumer data is ready
                        self.__event.set()

                    except BaseException:
                        self.__log_error("Unable to read serial data [%s]", b, exc_info=True)
                        time.sleep(1)

        except serial.serialutil.SerialException as e:
            self.__log_error("Unable to open serial port [%s]", e, exc_info=True)
            sys.exit(0)

        finally:
            if ser:
                ser.close()


    # Process data without doing a busy wait
    # If process_data() runs faster than read_serial_port(), it will wait on self.event
    def process_data(self, func, userdata):
        #print('got into process_data')
        while not self.__stopped:
            with PROCESS_TIME.time():
                try:
                    # Wait for data
                    #print("waiting for event")
                    self.__event.wait()
                    #print("the event happened")
                    # Reset event to trigger wait on net iteration
                    self.__event.clear()
                    # Read data with mutex
                    with self.__lock:
                        val = self.__data
                        #print("got the data")
                    # Call func with data

                    func(val, userdata)
                except BaseException as e:
                    self.__log_error("Error while calling func [%s]", e, exc_info=True)
                    # Do not sleep on errors and slow down sampling
                    # time.sleep(1)

    def start(self):
        # Start read_serial_port()
        Thread(target=self.read_serial_data, args=(self.__port_path, self.__baudrate)).start()
        #print("Start reading thread")
        # Start process_data()
        Thread(target=self.process_data, args=(self.__func, self.__userdata)).start()
        #print("Start publish thread")

        self.__stopped = False
        #print("Self.stopped is false")
        return self

    def stop(self):
        self.__stopped = True
        return self
    @staticmethod
    def lookup_port(did):
        """Get port info from a given DID"""
        #self.__log_info("Using DID = %s", did)
        ports = [p for p in serial.tools.list_ports.grep(did)]
        if len(ports) == 1:
            # PySerial v.2.7 is packaged along with raspis. It returns data from list_ports in the form of a tuple.
            # v.3.x is the latest, and it returns objects instead.
            port_info = ports[0]
            return port_info[0] if isinstance(port_info, tuple) else port_info.device

        #logger.error("%s matches found for device id %s", "No" if len(ports) == 0 else "Multiple", did)
        return None
    @staticmethod
    def all_ports():
        """Get all ports"""
        return [{DEVICE: p.device, MANF: p.manufacturer, HWID: p.hwid, SN: p.serial_number}
                for p in serial.tools.list_ports.grep(".*")]

    @staticmethod
    def metro_minis():
        """Get all Metro Mini ports"""
        return [p for p in SerialReader.all_ports() if p[MANF] == "Silicon Labs"]
