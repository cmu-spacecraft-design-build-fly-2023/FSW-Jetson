import numpy as np
import brahe
from scipy.linalg import expm
from flight.gnc import astrodynamics
from flight.gnc.utils import *


def sample_attitude() -> np.ndarray:
    """
    Samples a random attitude quaternion.

    Returns:
        np.ndarray: A random attitude quaternion.
    """
    r_axisangle = (np.random.rand(3) * 2 * np.pi) - np.pi
    θ_n = np.linalg.norm(r_axisangle)
    axis_n = r_axisangle / θ_n
    q = np.concatenate(([np.cos(0.5 * θ_n)], axis_n * np.sin(0.5 * θ_n)))
    return q


def sample_sun_synchronous_orbit(
    sma_lb=astrodynamics.R_EARTH + 450e3, sma_ub=astrodynamics.R_EARTH + 750e3
):
    """
    Samples a random sun-synchronous orbit.

    Args:
        sma_lb (float): Lower bound of semi-major axis.
        sma_ub (float): Upper bound of semi-major axis.

    Returns:
        np.ndarray: ECI state vector of the sampled orbit.
    """
    sma = sma_lb + np.random.rand() * (sma_ub - sma_lb)
    ecc = np.random.rand() * 0.0015
    i = brahe.sun_sync_inclination(sma, ecc)
    raan = np.random.rand() * 2 * np.pi
    omega = np.random.rand() * 2 * np.pi
    anomaly = np.random.rand() * 2 * np.pi
    eci_state = astrodynamics.get_CART_from_OSC(
        np.array([sma, ecc, i, raan, omega, anomaly])
    )
    return eci_state


def sample_sso_orbit_pos_near_landmark(landmarks, landmark_cone_angle=np.deg2rad(5)):
    """
    Samples a random sun-synchronous orbit position near a landmark.

    Args:
        landmarks (np.ndarray): Array of landmarks.
        landmark_cone_angle (float): Cone angle for landmark acceptance.

    Returns:
        np.ndarray: ECI state vector of the sampled orbit position.
    """
    mean_landmark = np.mean(landmarks, axis=0)
    ra = sample_sun_synchronous_orbit()[:3]
    while (
        np.dot(mean_landmark / np.linalg.norm(mean_landmark), ra / np.linalg.norm(ra))
        < np.cos(landmark_cone_angle)
        or (np.linalg.norm(ra) > (astrodynamics.R_EARTH + 750e3))
        or (np.linalg.norm(ra) < (astrodynamics.R_EARTH + 450e3))
    ):  # mission specific
        ra = sample_sun_synchronous_orbit()[:3]
    return ra


def sample_attitude_hemisphere(direction, ang_step=np.deg2rad(20)):
    """
    Sample N points on the direction hemisphere.
    """
    if np.array_equal(direction, [0, 0, 1]):
        longitude_range = np.arange(0, np.pi / 2 + ang_step, ang_step)
        latitude_range = np.arange(0, 2 * np.pi + ang_step, ang_step)

    elif np.array_equal(direction, [0, 0, -1]):
        longitude_range = np.arange(np.pi / 2, np.pi + ang_step, ang_step)
        latitude_range = np.arange(0, 2 * np.pi + ang_step, ang_step)

    elif np.array_equal(direction, [1, 0, 0]):
        longitude_range = np.arange(0, np.pi + ang_step, ang_step)
        latitude_range = np.arange(-np.pi / 2, np.pi / 2 + ang_step, ang_step)

    elif np.array_equal(direction, [-1, 0, 0]):
        longitude_range = np.arange(0, np.pi + ang_step, ang_step)
        latitude_range = np.arange(np.pi / 2, 3 * np.pi / 2 + ang_step, ang_step)

    elif np.array_equal(direction, [0, 1, 0]):
        longitude_range = np.arange(0, np.pi + ang_step, ang_step)
        latitude_range = np.arange(0, np.pi + ang_step, ang_step)

    elif np.array_equal(direction, [0, -1, 0]):
        longitude_range = np.arange(0, np.pi + ang_step, ang_step)
        latitude_range = np.arange(np.pi, 2 * np.pi + ang_step, ang_step)

    Pt = np.array([0, 0, 1])

    nb = len(longitude_range) * len(latitude_range)
    print(len(longitude_range))
    print(len(latitude_range))
    Q_samples = np.zeros((nb, 3, 3))

    idx = 0
    print(nb)
    for theta in longitude_range:
        for phi in latitude_range:
            x = np.sin(theta) * np.cos(phi)
            y = np.sin(theta) * np.sin(phi)
            z = np.cos(theta)
            v = np.array([x, y, z])
            Q_samples[idx, :, :] = to_rotation_matrix(v)
            if np.dot(direction, Q_samples[idx, :, :] @ Pt) < 0:  # reject
                continue
            idx += 1

    return Q_samples[:idx, :, :]


def sample_rotation_matrices(P, Q_samples, direction_hemisphere, Q0=np.eye(3)):
    """
    Samples rotation matrices with desired covariance within the direction hemisphere.

    Args:
        P (np.ndarray): Covariance matrix.
        Q_samples (np.ndarray): Array to store the samples.
        direction_hemisphere (np.ndarray): Direction hemisphere vector.
        Q0 (np.ndarray): Initial rotation matrix.

    Returns:
        None
    """
    Δ = np.linalg.cholesky(P)
    Pt = np.array([0, 0, 1])
    for k in range(Q_samples.shape[0]):
        ϕ = Δ @ np.random.randn(3)
        Q_samples[k, :, :] = Q0 @ expm(skew_symmetric(ϕ))
        while (
            np.dot(direction_hemisphere, Q_samples[k] @ Pt) < 0
        ):  # Reject samples outside the direction hemisphere
            ϕ = Δ @ np.random.randn(3)
            Q_samples[k, :, :] = Q0 @ expm(skew_symmetric(ϕ))
