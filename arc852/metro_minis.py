#!/usr/bin/env python

from arc852.serial_reader import SerialReader, DEVICE, HWID, SN, MANF


def main():
    for p in SerialReader.metro_minis():
        print("Manufacturer: " + p[MANF])
        print("HWID: " + p[HWID])
        print("Device: " + p[DEVICE])
        print("SN: " + p[SN])
        print("\n")


if __name__ == "__main__":
    main()
