class Scale:
    def __init__(self, old_min, old_max, new_min, new_max):
        self.old_min = old_min
        self.old_max = old_max
        self.new_min = new_min
        self.new_max = new_max
        assert old_min != old_max
        assert new_min != new_max
        assert old_min < old_max
        assert new_min < new_max

    def translate(self, value):
        oldSpan = self.old_max - self.old_min
        newSpan = self.new_max - self.new_min

        # Convert to 0-1 range
        value01 = float(value - self.old_min) / float(oldSpan)

        # Convert to the new_range
        valueScaled = self.new_min + (value01 * newSpan)
        return valueScaled





