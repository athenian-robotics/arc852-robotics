import time


class PIDControl:
    """
    PID Control based on existing code in Java.
    Depending on your implementation, you will most likely only need to really worry about
    P, but I and D can be useful on their own as well.
    """

    def __init__(self, p, i, d, upper_bound=None, lower_bound=None, reversed_constants=False,
                 reading_timeout=-1):

        self.p_gain = p
        self.i_gain = i
        self.d_gain = d

        self._error_sum = 0
        self._last_error = 0

        self._i_sum = 0
        self._max_error = 0
        self._max_i = 0

        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        self._last_reading_timestamp = -1
        self.reading_timeout = reading_timeout

        if reversed_constants:
            self.reverse_constants()

    def __str__(self):
        return "P: {}, I: {}, D: {}".format(self.p_gain, self.i_gain, self.d_gain)

    def reset_sum(self):
        """Reset the error for integral sum so it doesn't run away"""
        self._error_sum = 0

    def reverse_constants(self):
        self.p_gain *= 1.0
        self.i_gain *= 1.0
        self.d_gain *= 1.0

    @staticmethod
    def _constrain(input_amount, lower_bound, upper_bound):
        if upper_bound is not None and input_amount > upper_bound:
            return upper_bound
        elif lower_bound is not None and input_amount < lower_bound:
            return lower_bound
        else:
            return input_amount

    def get_pid(self, error):
        # Reset I if it's been too long since we last read
        if 0 <= self.reading_timeout < (time.time() - self._last_reading_timestamp):
            self.reset_sum()

        p_out = self.p_gain * float(error)

        # The integral can be approximated with the sum of the error
        i_out = self.i_gain * self._error_sum

        if self._max_i != 0:
            # We might want to constrain I within some bounds so that it doesn't run wild.
            i_out = self._constrain(i_out, -self._max_i, self._max_i)

        # d is the rate of change, and can be approximated by taking the difference in errors
        d_out = (error - self._last_error) * -float(self.d_gain)

        self._last_error = error

        output = p_out + i_out + d_out

        if self.lower_bound is not None or self.upper_bound is not None:
            output = self._constrain(output, self.lower_bound, self.upper_bound)

        if self._max_i is not None:
            self._error_sum = self._constrain(self._error_sum + error, -self._max_error, self._max_error)
        else:
            self._error_sum += error

        self._last_reading_timestamp = time.time()

        return output
