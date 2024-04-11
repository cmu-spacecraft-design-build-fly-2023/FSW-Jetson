import numpy as np
from flight.gnc import triangulation
from flight.gnc.utils import *


def inc(x):
    return x + 1


def test_answer():
    assert inc(3) == 4