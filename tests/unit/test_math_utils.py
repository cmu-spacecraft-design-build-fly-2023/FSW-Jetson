import numpy as np
from numpy.testing import assert_array_almost_equal

from flight.gnc.math_utils import (
    dcm_from_q,
    rotm2quat,
    geodesic_distance,
    L,
    R,
    conj,
    skew_symmetric,
)
import pytest


@pytest.mark.parametrize(
    "q, expected_dcm",
    [
        (np.array([1, 0, 0, 0]), np.identity(3)),  # Identity quaternion
        (np.array([2, 0, 0, 0]), np.identity(3)),  # Unnormalized identity quaternion
        (np.array([-1, -1, -1, -1]), None),  # Negative quaternion
    ],
)
def test_dcm_from_q(q, expected_dcm):
    if np.all(q == -1):
        expected_dcm = dcm_from_q(
            np.array([1, 1, 1, 1])
        )  # Negative should yield the same DCM as positive
    dcm = dcm_from_q(q)
    assert_array_almost_equal(dcm, expected_dcm)


@pytest.mark.parametrize("q", [(np.array([0, 0, 0, 0]))])  # Zero quaternion
def test_dcm_from_q_zero_quaternion(q):
    with pytest.raises(ZeroDivisionError):
        dcm_from_q(q)


@pytest.mark.parametrize(
    "R, expected_quat",
    [
        (np.identity(3), np.array([1, 0, 0, 0])),  # Identity rotation
        (
            np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]]),
            np.array([0.7071068, 0, 0, 0.7071068]),
        ),  # 90 deg about z
        (
            np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]]),
            np.array([0, 1, 0, 0]),
        ),  # 180 deg about x
    ],
)
def test_rotm2quat(R, expected_quat):
    quat = rotm2quat(R)
    assert_array_almost_equal(quat, expected_quat)


@pytest.mark.parametrize(
    "q1, q2, expected_distance",
    [
        (np.array([1, 0, 0, 0]), np.array([1, 0, 0, 0]), 0),
        (np.array([1, 0, 0, 0]), np.array([-1, 0, 0, 0]), 0),
        (
            np.array([0.76834982, 0.5488213, -0.32929278, 0.0]),
            np.array([0.61999852, 0.0, -0.75151336, -0.22545401]),
            0.2761563263964585,
        ),
    ],
)
def test_geodesic_distance(q1, q2, expected_distance):
    distance = geodesic_distance(q1, q2)
    assert np.isclose(distance, expected_distance)


@pytest.mark.parametrize(
    "q, expected_L",
    [
        (
            np.array([1, 0, 0, 0]),
            np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]),
        ),  # Identity quaternion
        (
            np.array([np.sqrt(0.5), np.sqrt(0.5), 0, 0]),
            np.array(
                [
                    [np.sqrt(0.5), -np.sqrt(0.5), 0, 0],
                    [np.sqrt(0.5), np.sqrt(0.5), 0, 0],
                    [0, 0, np.sqrt(0.5), -np.sqrt(0.5)],
                    [0, 0, np.sqrt(0.5), np.sqrt(0.5)],
                ]
            ),
        ),  # 90 degree rotation around x-axis
    ],
)
def test_L(q, expected_L):
    result_L = L(q)
    assert_array_almost_equal(result_L, expected_L)


@pytest.mark.parametrize(
    "q, expected_R",
    [
        (
            np.array([1, 0, 0, 0]),
            np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]),
        ),  # Identity quaternion
        (
            np.array([np.sqrt(0.5), np.sqrt(0.5), 0, 0]),
            np.array(
                [
                    [np.sqrt(0.5), -np.sqrt(0.5), 0, 0],
                    [np.sqrt(0.5), np.sqrt(0.5), 0, 0],
                    [0, 0, np.sqrt(0.5), np.sqrt(0.5)],
                    [0, 0, -np.sqrt(0.5), np.sqrt(0.5)],
                ]
            ),
        ),  # 90 degree rotation around x-axis
    ],
)
def test_R(q, expected_R):
    result_R = R(q)
    assert_array_almost_equal(result_R, expected_R)


@pytest.mark.parametrize(
    "q, expected_conj",
    [
        (
            np.array([0.9031747, 0.0168863, -0.0759882, 0.4221566]),
            np.array([0.9031747, -0.0168863, 0.0759882, -0.4221566]),
        )
    ],
)
def test_conj(q, expected_conj):
    result_conj = conj(q)
    assert_array_almost_equal(result_conj, expected_conj)


@pytest.mark.parametrize(
    "w, expected_matrix",
    [(np.array([1, 2, 3]), np.array([[0, -3, 2], [3, 0, -1], [-2, 1, 0]]))],
)
def test_skew_symmetric(w, expected_matrix):
    result_matrix = skew_symmetric(w)
    assert_array_almost_equal(result_matrix, expected_matrix)
