from collections import deque

from numpy import average


class MovingAverage(object):
    def __init__(self, size=10):
        self._max_size = size
        self.values = deque(maxlen=size)

    def add(self, val):
        if val:
            self.values.append(val)

    def average(self):
        return average(self.values) if len(self.values) > 0 else None

    def max_size(self):
        return self._max_size

    def size(self):
        return len(self.values)

    def clear(self):
        self.values.clear()
