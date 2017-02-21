from collections import deque

from utils import current_time_millis


class BadValuesQueue(object):
    def __init__(self, size=5):
        self.values = deque(maxlen=size)
        self._size = size

    def mark(self):
        self.values.append(current_time_millis())

    def is_invalid(self, max_elapsed_time):
        if len(self.values) < self._size:
            return False
        else:
            return abs(self.values[0] - self.values[-1]) > max_elapsed_time

    def clear(self):
        self.values.clear()
