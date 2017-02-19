from collections import deque

from numpy import average


class MovingAverage(object):
    def __init__(self, size=10):
        self.values = deque(maxlen=size)

    def add(self, val):
        self.values.append(val)

    def average(self):
        if len(self.values) <= 1:
            return None
        return average(self.values)

    def clear(self):
        self.values.clear()
