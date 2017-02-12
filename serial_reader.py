import logging
import sys
import time
from threading import Event
from threading import Lock
from threading import Thread

import serial
from utils import is_windows

DEFAULT_BAUD = 115200

logger = logging.getLogger(__name__)


class SerialReader(object):
    def __init__(self):
        self.lock = Lock()
        self.event = Event()
        self.stopped = False
        self.data = None

    # Read data from serial port and pass it along to the consumer
    # If the consumer runs slower than the producer, then values will be dropped
    def read_serial_port(self, port, baudrate):
        ser = None
        try:
            # Open serial port
            ser = serial.Serial(port=port, baudrate=baudrate)
            logger.info("Reading data from serial port {0} at {1}bps".format(port, baudrate))

            while not self.stopped:
                try:
                    # Read data from serial port.  Ignore the trailing two chars with [:-2]
                    # Do not call readline() inside mutex because it might block
                    b = ser.readline()[:-2]

                    # Update data with mutex
                    with self.lock:
                        self.data = b.decode("utf-8")

                    # Notify consumer data is ready
                    self.event.set()

                except BaseException as e:
                    logger.error("Unable to read serial data [{0}]".format(e), exc_info=True)
                    time.sleep(1)

        except serial.serialutil.SerialException as e:
            logger.error("Unable to open serial port [{0}]".format(e), exc_info=True)
            sys.exit(0)

        finally:
            if ser is not None:
                ser.close()

    # Process data without doing a busy wait
    # If process_data() runs faster than read_serial_port(), it will wait on self.event
    def process_data(self, func, userdata):
        while not self.stopped:
            try:
                # Wait for data
                self.event.wait()

                # Reset event to trigger wait on net iteration
                self.event.clear()

                # Read data with mutex
                with self.lock:
                    val = self.data

                # Call func with data
                func(val, userdata)

            except BaseException as e:
                logger.error("Error while calling func [{0}]".format(e), exc_info=True)
                # Do not sleep on errors and slow down sampling
                # time.sleep(1)

    def start(self, func, userdata=None, port="/dev/ttyACM0", baudrate=DEFAULT_BAUD):
        # Start read_serial_port()
        port_path = ("" if (is_windows() or "/dev/" in str(port)) else "/dev/") + str(port)
        Thread(target=self.read_serial_port, args=(port_path, baudrate)).start()

        # Start process_data()
        Thread(target=self.process_data, args=(func, userdata)).start()

        self.stopped = False

    def stop(self):
        self.stopped = True
