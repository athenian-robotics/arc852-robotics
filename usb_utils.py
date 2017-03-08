import re
import subprocess

__DEVICE_NUM = "device_num"


def usb_devices():
    device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb")
    for line in df.split("\n"):
        if line:
            info = device_re.match(line)
            if info:
                dinfo = info.groupdict()
                bus = dinfo.pop("bus")
                device_num = dinfo.pop("device")
                dinfo["device"] = "/dev/bus/usb/%s/%s" % (bus, device_num)
                dinfo[__DEVICE_NUM] = int(device_num)
                yield dinfo


def lookup_device(did):
    for i in usb_devices():
        if i["id"] == did:
            return i[__DEVICE_NUM]
