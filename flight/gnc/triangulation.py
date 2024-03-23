import numpy as np

from flight.gnc import sampling
from flight.gnc.utils import *


def compute_nadir_vector(orbit_pos):
    """
    Compute the nadir vector given the spacecraft position.

    Args:
        orbit_pos (np.ndarray): Array representing the spacecraft position.

    Returns:
        np.ndarray: Nadir vector.
    """
    return -orbit_pos / np.linalg.norm(orbit_pos)


def nadir_pointing_attitude(vec_to_align, nadir_dir):
    """
    Get the quaternion representing the nadir pointing attitude.

    Args:
        vec_to_align (np.ndarray): Vector to align.
        nadir_dir (np.ndarray): Nadir direction.

    Returns:
        np.ndarray: Quaternion representing the nadir pointing attitude.
    """
    c = np.cross(vec_to_align, nadir_dir)
    n = c / np.linalg.norm(c)
    theta = np.arctan2(np.linalg.norm(c), np.dot(vec_to_align, nadir_dir))
    dq = np.array([np.cos(theta/2), *n*np.sin(theta/2)])
    dq = dq / np.linalg.norm(dq)
    return dq


def triangulate_orbit_position(landmarks, measurements, Q0, Als=None, bls=None):
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
    temp = np.dot(Q0, measurements.T)
    
    sz = measurements.shape[0]
    skew_v_eci = np.zeros((3, 3))

    if Als is None or bls is None:
        Als = np.zeros((3 * sz, 3))
        bls = np.zeros((3 * sz, 1))

    # Form linear system
    for i in range(sz):
        skew_v_eci[:, :] = skew_symmetric(temp[:, i])
        Als[i*3:i*3+3, :] = skew_v_eci
        bls[i*3:i*3+3, 0] = np.dot(skew_v_eci, landmarks[i, :])
    
    # Solve least-squares w/ QR decomposition
    Q, Rr = np.linalg.qr(Als)
    x = np.linalg.solve(Rr, np.dot(Q[:, :3].T, bls))
    
    cost = np.linalg.norm(np.dot(Als, x) - bls)
    return x.flatten(), cost


def sample_attitude_hemisphere(direction, ang_step=np.deg2rad(20)):
    """
    Sample N points on the direction hemisphere.

    Args:
        direction (np.ndarray): Direction vector.
        ang_step (float, optional): Angular step size. Defaults to np.deg2rad(20).

    Returns:
        np.ndarray: Array of sampled attitude quaternions.
    """
    if np.array_equal(direction, [0, 0, 1]):
        longitude_range = np.arange(0, np.pi/2 + ang_step, ang_step)
        latitude_range = np.arange(0, 2*np.pi + ang_step, ang_step)
    elif np.array_equal(direction, [0, 0, -1]):
        longitude_range = np.arange(np.pi/2, np.pi + ang_step, ang_step)
        latitude_range = np.arange(0, 2*np.pi + ang_step, ang_step)
    elif np.array_equal(direction, [1, 0, 0]):
        longitude_range = np.arange(0, np.pi + ang_step, ang_step)
        latitude_range = np.arange(-np.pi/2, np.pi/2 + ang_step, ang_step)
    elif np.array_equal(direction, [-1, 0, 0]):
        longitude_range = np.arange(0, np.pi + ang_step, ang_step)
        latitude_range = np.arange(np.pi/2, 3*np.pi/2 + ang_step, ang_step)
    elif np.array_equal(direction, [0, 1, 0]):
        longitude_range = np.arange(0, np.pi + ang_step, ang_step)
        latitude_range = np.arange(0, np.pi + ang_step, ang_step)
    elif np.array_equal(direction, [0, -1, 0]):
        longitude_range = np.arange(0, np.pi + ang_step, ang_step)
        latitude_range = np.arange(np.pi, 2*np.pi + ang_step, ang_step)
    

    Pt = np.array([0, 0, 1])

    nb = len(longitude_range) * len(latitude_range)
    Q_samples = np.zeros((nb, 3, 3))

    idx = 0
    
    for theta in longitude_range:
        for phi in latitude_range:
            x = np.sin(theta) * np.cos(phi)
            y = np.sin(theta) * np.sin(phi)
            z = np.cos(theta)
            v = np.array([x, y, z])
            Q_samples[idx, :, :] = to_rotation_matrix(v)
            if np.dot(direction, np.dot(Q_samples[idx, :, :], Pt)) < 0:  # reject
                continue
            idx += 1
            
    return Q_samples[:idx, :, :]


def sampling_search(landmarks, 
                    measurements, 
                    Q_start, 
                    camera_direction, 
                    N_samples=30, 
                    initial_angular_sampling_step=np.deg2rad(2), 
                    decay=0.9, 
                    max_iterations=100, 
                    verbose=False):
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
    curr_cost = np.inf
    sz = measurements.shape[0]
    Als = np.zeros((3 * sz, 3))
    bls = np.zeros((3 * sz, 1))
    P_cr = (initial_angular_sampling_step ** 2) * np.eye(3)
    
    # Initial Grid Sampling
    Q_samples = sample_attitude_hemisphere(camera_direction, np.deg2rad(5))
    ns = Q_samples.shape[0]
    r_samples = np.zeros((ns, 3))
    cost_samples = np.zeros(ns)


    for k in range(ns):
        r_samples[k, :], cost_samples[k] = triangulate_orbit_position(landmarks, measurements, Q_samples[k], Als, bls)
                                                    
    # Take the lowest cost attitude
    idx = np.argmin(cost_samples)
    if cost_samples[idx] < curr_cost:
        curr_cost = cost_samples[idx]
        Qi = Q_samples[idx, :, :]
        ri = r_samples[idx]
    
    # Print current cost
    if verbose:
        print("Cost after grid sampling: ", curr_cost)
    
    
    for i in range(max_iterations): ## TODO - other stopping condition based on cost reduction
        P_cr = P_cr * decay

        # TODO pre-allocate but handle the case where the number of samples is less than N_samples (rejection sampling)
        Q_samples = np.zeros((N_samples, 3, 3))
        r_samples = np.zeros((N_samples, 3))
        cost_samples = np.zeros(N_samples)

        # Sample rotation matrices
        sampling.sample_rotation_matrices(P_cr, Q_samples, camera_direction, Q0=Qi)
        
        # Triangulate for each sample
        for k in range(N_samples):
            r_samples[k, :], cost_samples[k] = triangulate_orbit_position(landmarks, measurements, Q_samples[k], Als, bls)
                
        # Take the lowest cost attitude
        idx = np.argmin(cost_samples)
        if cost_samples[idx] < curr_cost:
            curr_cost = cost_samples[idx]
            Qi = Q_samples[idx]
            ri = r_samples[idx]
        
        # Verbose printing
        if verbose:
            print(f"Iteration {i}, cost: {curr_cost}")

    return ri, Qi, curr_cost


