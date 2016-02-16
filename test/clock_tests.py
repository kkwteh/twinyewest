from unittest import TestCase
from twinsies.clock import twinsy_finder

class ClockTests(TestCase):
    def test_twinsy_finder(self):
        res = twinsy_finder(fetch_size=2)
