import unittest
from arc852.scale_values import Scale


class TestScale(unittest.TestCase):

    def test_scale(self):
        scale = Scale(-1, 1, 0, 5)
        self.assertEqual(scale.translate(0), 2.5)
        self.assertEqual(scale.translate(0.5), 3.75)
        with self.assertRaises(AssertionError):
            scale = Scale(1, 1, 1, 1)
        with self.assertRaises(AssertionError):
            scale = Scale(2, 1, 1, -4)
        scale = Scale(-5, -2, 0, 5)
        self.assertEqual(scale.translate(-3.5), 2.5)
        scale = Scale(0, 1, -0.5, 0.5)
        self.assertEqual(scale.translate(0.5), 0)
