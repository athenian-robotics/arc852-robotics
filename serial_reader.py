import sys
import time
import traceback
from threading import Event
from threading import Lock
from threading import Thread

import serial
from common_utils import is_windows

DEFAULT_BAUD = 115200


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

            while not self.stopped:
                try:
                    # Read data from serial port.  Ignore the trailing two chars with [:-2]
                    # Do not call readline() inside mutex because it might block
                    bytes = ser.readline()[:-2]

                    # Update data with mutex
                    with self.lock:
                        self.data = bytes.decode("utf-8")

                    # Notify consumer data is ready
                    self.event.set()

                except BaseException as e:
                    print(e)
                    time.sleep(1)

        except serial.serialutil.SerialException as e:
            traceback.print_exc()
            sys.exit(0)

        finally:
            if ser is not None:
                ser.close()

    # Process data without doing a busy wait
    # If process_data() runs faster than read_serial_port(), it will wait on self.event
    def process_data(self, func):
        while not self.stopped:
            try:
                # Wait for data
                self.event.wait()

                # Reset event to trigger wait on net iteration
                self.event.clear()

                # Read data with mutex
                with self.lock:
                    tuple = eval(self.data)

                # Call func with data
                func(tuple)

            except BaseException as e:
                traceback.print_exc()
                time.sleep(1)

    def start(self, func, port, baudrate=DEFAULT_BAUD):
        # Start read_serial_port()
        port_path = ("" if is_windows() or "/dev/" in port else "/dev/") + port
        Thread(target=self.read_serial_port, args=(port_path, baudrate)).start()

        # Start process_data()
        Thread(target=self.process_data, args=(func,)).start()

        self.stopped = False

    def stop(self):
        self.stopped = True
