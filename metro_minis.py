#!/usr/bin/env python

from serial_reader import SerialReader

if __name__ == "__main__":
    for p in SerialReader.metro_minis():
        print(p)
