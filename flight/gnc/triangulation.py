import numpy as np

from flight.gnc import sampling
from flight.gnc.utils import *
from typing import Tuple
import numpy as np


def compute_nadir_vector(orbit_pos: np.ndarray) -> np.ndarray:
    """
    Compute the nadir vector given the spacecraft position.

    Args:
        orbit_pos (np.ndarray): Array representing the spacecraft position.

    Returns:
        np.ndarray: Nadir vector.
    """
    norm = np.linalg.norm(orbit_pos)
    if norm == 0:
        raise ValueError("Invalid orbit position: norm is zero.")
    return -orbit_pos / norm


def nadir_pointing_attitude(
    vec_to_align: np.ndarray, nadir_dir: np.ndarray
) -> np.ndarray:
    """
    Get the quaternion representing the nadir pointing attitude.

    Args:
        vec_to_align (np.ndarray): Vector to align.
        nadir_dir (np.ndarray): Nadir direction.

    Returns:
        np.ndarray: Quaternion representing the nadir pointing attitude.
    """
    norm_vec_to_align = np.linalg.norm(vec_to_align)
    norm_nadir_dir = np.linalg.norm(nadir_dir)

    if norm_vec_to_align == 0 or norm_nadir_dir == 0:
        raise ValueError("Invalid input vectors: norm is zero.")

    vec_to_align_normalized = vec_to_align / norm_vec_to_align
    nadir_dir_normalized = nadir_dir / norm_nadir_dir

    c = np.cross(vec_to_align_normalized, nadir_dir_normalized)
    n = c / np.linalg.norm(c)
    theta = np.arctan2(
        np.linalg.norm(c), np.dot(vec_to_align_normalized, nadir_dir_normalized)
    )
    dq = np.hstack((np.cos(theta / 2), n * np.sin(theta / 2)))
    dq = dq / np.linalg.norm(dq)
    return dq


def triangulate_orbit_position(
    landmarks: np.ndarray,
    measurements: np.ndarray,
    Q0: np.ndarray,
    Als: np.ndarray = None,
    bls: np.ndarray = None,
) -> Tuple[np.ndarray, float]:
    """
    3D triangulation using an estimated attitude to find the spacecraft position.
    It solves a least-squares problem minimizing the differences between the line of position vectors (N^r = N^l + rho * N^v where rho is a scalar that can take any value)

    Args:
        landmarks (np.ndarray): Array of landmarks.
        measurements (np.ndarray): Array of measurements.
        Q0 (np.ndarray): Initial attitude estimate.
        Als (np.ndarray, optional): Linear system matrix. Defaults to None.
        bls (np.ndarray, optional): Linear system vector. Defaults to None.

    Returns:
        Tuple[np.ndarray, float]: Tuple containing the spacecraft position and the cost.
    """
    # Transform observation in ECI frame
    temp = Q0 @ measurements.T
    sz = measurements.shape[0]
    skew_v_eci = np.zeros((3, 3))
    if Als is None or bls is None:
        Als = np.zeros((3 * sz, 3))
        bls = np.zeros((3 * sz, 1))
    # Form linear system
    for i in range(sz):
        skew_v_eci[:, :] = skew_symmetric(temp[:, i])
        Als[i * 3 : i * 3 + 3, :] = skew_v_eci
        bls[i * 3 : i * 3 + 3, 0] = skew_v_eci @ landmarks[i, :]
    # Solve least-squares w/ QR decomposition
    Q, Rr = np.linalg.qr(Als)
    x = np.linalg.solve(Rr, Q[:, :3].T @ bls)
    cost = np.linalg.norm(Als @ x - bls)
    return x.flatten(), cost


def sampling_search(
    landmarks: np.ndarray,
    measurements: np.ndarray,
    Q_start: np.ndarray,
    camera_direction: np.ndarray,
    N_samples: int = 30,
    initial_angular_sampling_step: float = np.deg2rad(1),
    decay: float = 0.9,
    max_iterations: int = 100,
    verbose: bool = False,
) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Perform sampling search to find the spacecraft orbit position.

    Args:
        landmarks (np.ndarray): Array of landmarks.
        measurements (np.ndarray): Array of measurements.
        Q_start (np.ndarray): Initial attitude estimate.
        camera_direction (np.ndarray): Camera direction.
        N_samples (int, optional): Number of samples. Defaults to 30.
        initial_angular_sampling_step (float, optional): Initial angular sampling step. Defaults to np.deg2rad(2).
        decay (float, optional): Decay factor. Defaults to 0.9.
        max_iterations (int, optional): Maximum number of iterations. Defaults to 100.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    Returns:
        Tuple[np.ndarray, np.ndarray, float]: Tuple containing the spacecraft position, attitude estimate, and cost.
    """
    # Initialize variables
    Qi = Q_start
    ri = np.zeros(3)
    sz = measurements.shape[0]
    Als = np.zeros((3 * sz, 3))
    bls = np.zeros((3 * sz, 1))
    curr_cost = np.inf
    # Initial Grid Sampling
    Q_samples = sampling.sample_attitude_hemisphere(camera_direction, np.deg2rad(5))
    ns = Q_samples.shape[0]
    r_samples = np.zeros((ns, 3))
    cost_samples = np.zeros(ns)
    for k in range(ns):
        r_samples[k, :], cost_samples[k] = triangulate_orbit_position(
            landmarks, measurements, Q_samples[k], Als, bls
        )
    # Take the lowest cost attitude
    idx = np.argmin(cost_samples)
    if cost_samples[idx] < curr_cost:
        curr_cost = cost_samples[idx]
        Qi = Q_samples[idx, :, :]
        ri = r_samples[idx, :]
    # Print current cost
    if verbose:
        print("Cost after grid sampling: ", curr_cost)
    P_cr = (initial_angular_sampling_step**2) * np.eye(3)
    for i in range(
        max_iterations
    ):  ## TODO - other stopping condition based on cost reduction
        P_cr = P_cr * decay
        # TODO pre-allocate but handle the case where the number of samples is less than N_samples (rejection sampling)
        Q_samples = np.zeros((N_samples, 3, 3))
        r_samples = np.zeros((N_samples, 3))
        cost_samples = np.zeros(N_samples)
        # Sample rotation matrices
        sampling.sample_rotation_matrices(P_cr, Q_samples, camera_direction, Q0=Qi)
        # Triangulate for each sample
        for k in range(N_samples):
            r_samples[k, :], cost_samples[k] = triangulate_orbit_position(
                landmarks, measurements, Q_samples[k], Als, bls
            )
        # Take the lowest cost attitude
        idx = np.argmin(cost_samples)
        if cost_samples[idx] < curr_cost:
            curr_cost = cost_samples[idx]
            Qi = Q_samples[idx, :, :]
            ri = r_samples[idx, :]
        # Verbose printing
        if verbose:
            print(f"Iteration {i}, cost: {curr_cost}")
    return ri, Qi, curr_cost
