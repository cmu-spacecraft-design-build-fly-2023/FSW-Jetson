import numpy as np
from flight.gnc.triangulation import compute_nadir_vector, nadir_pointing_attitude

import pytest


@pytest.mark.parametrize("orbit_pos, expected_result", [
    (np.array([1, 2, 3]), np.array([-0.26726124, -0.53452248, -0.80178373])),
    (np.array([0, 0, 0]), "raises")
])
def test_compute_nadir_vector(orbit_pos, expected_result):
    if isinstance(expected_result, str) and expected_result == "raises":
        with pytest.raises(ValueError):
            compute_nadir_vector(orbit_pos)
    else:
        assert np.allclose(compute_nadir_vector(orbit_pos), expected_result)


@pytest.mark.parametrize("vec_to_align, nadir_dir, expected_result", [
    (np.array([1, 0, 0]), np.array([0, 0, -1]), np.array([0.70710678, 0, 0.70710678, 0])),
    (np.array([0, 1, 0]), np.array([0, 0, -1]), np.array([0.70710678, -0.70710678, 0, 0])),
    (np.array([0, 0, 0]), np.array([1, 1, 1]), "raises")
])
def test_nadir_pointing_attitude(vec_to_align, nadir_dir, expected_result):
    if isinstance(expected_result, str) and expected_result == "raises":
        with pytest.raises(ValueError):
            nadir_pointing_attitude(vec_to_align, nadir_dir)
    else:
        assert np.allclose(nadir_pointing_attitude(vec_to_align, nadir_dir), expected_result)


