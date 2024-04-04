import numpy as np
from scipy.linalg import expm, cholesky


def dcm_from_q(q):
    """
    Convert a quaternion to a direction cosine matrix (DCM).

    Args:
        q (np.ndarray): Quaternion [q0, q1, q2, q3].

    Returns:
        np.ndarray: Direction cosine matrix (DCM).
    """
    norm = np.linalg.norm(q)
    q0, q1, q2, q3 = q / norm if norm != 0 else q

    # DCM
    Q = np.array(
        [
            [
                2 * q1**2 + 2 * q0**2 - 1,
                2 * (q1 * q2 - q3 * q0),
                2 * (q1 * q3 + q2 * q0),
            ],
            [
                2 * (q1 * q2 + q3 * q0),
                2 * q2**2 + 2 * q0**2 - 1,
                2 * (q2 * q3 - q1 * q0),
            ],
            [
                2 * (q1 * q3 - q2 * q0),
                2 * (q2 * q3 + q1 * q0),
                2 * q3**2 + 2 * q0**2 - 1,
            ],
        ]
    )

    return Q


def rotm2quat(r):
    """
    Convert a rotation matrix to a quaternion.

    Args:
        r (np.ndarray): Rotation matrix.

    Returns:
        np.ndarray: Quaternion [q0, q1, q2, q3].
    """
    q = np.zeros(4)
    q[0] = 0.5 * np.sqrt(1 + r[0, 0] + r[1, 1] + r[2, 2])
    q[1] = (1 / (4 * q[0])) * (r[2][1] - r[1][2])
    q[2] = (1 / (4 * q[0])) * (r[0][2] - r[2][0])
    q[3] = (1 / (4 * q[0])) * (r[1][0] - r[0][1])
    return np.array(q)


def geodesic_distance(q1, q2):
    """
    Compute the geodesic distance between two quaternions.

    Args:
        q1 (np.ndarray): Quaternion [q0, q1, q2, q3].
        q2 (np.ndarray): Quaternion [q0, q1, q2, q3].

    Returns:
        float: Geodesic distance between q1 and q2.
    """
    return 1 - abs(np.dot(q1, q2))


def random_rotation_matrix(P, Q0=np.diag(np.ones(3))):
    """
    Generate a random rotation matrix.

    Args:
        P (np.ndarray): Covariance matrix.
        Q0 (np.ndarray): Initial rotation matrix.

    Returns:
        np.ndarray: Random rotation matrix.
    """
    Δ = cholesky(P, lower=True)
    ϕ = Δ @ np.random.randn(3, 1)
    rot = Q0 @ expm(skew_symmetric(ϕ))
    return rot


def L(q):
    """
    Left-multiply a quaternion.

    Args:
        q (np.ndarray): Quaternion [q0, q1, q2, q3].

    Returns:
        np.ndarray: Left-multiplied quaternion.
    """
    L = np.zeros((4, 4))
    L[0, 0] = q[0]
    L[0, 1:] = -q[1:]
    L[1:, 0] = q[1:]
    L[1:, 1:] = q[0] * np.identity(3) + skew_symmetric(q[1:])
    return L


def R(q):
    """
    Right-multiply a quaternion.

    Args:
        q (np.ndarray): Quaternion [q0, q1, q2, q3].

    Returns:
        np.ndarray: Right-multiplied quaternion.
    """
    R = np.zeros((4, 4))
    R[0, 0] = q[0]
    R[0, 1:] = -q[1:]
    R[1:, 0] = q[1:]
    R[1:, 1:] = q[0] * np.identity(3) - skew_symmetric(q[1:])
    return R


def conj(q):
    """
    Compute the conjugate of a quaternion.

    Args:
        q (np.ndarray): Quaternion [q0, q1, q2, q3].

    Returns:
        np.ndarray: Conjugate of the quaternion.
    """
    qr = np.zeros(4)
    qr[0] = q[0]
    qr[1:] = -q[1:]
    return qr


def skew_symmetric(w):
    """
    Compute the skew symmetric form of a vector.

    Args:
        w (np.ndarray): Vector [w1, w2, w3].

    Returns:
        np.ndarray: Skew symmetric matrix.
    """
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])


def to_rotation_matrix(v):
    """
    Convert a vector to a rotation matrix.

    Args:
        v (np.ndarray): Vector [v1, v2, v3].

    Returns:
        np.ndarray: Rotation matrix.
    """
    # Axis of rotation (cross product with z-axis)
    axis = np.cross(v, [0, 0, 1])
    angle = np.arccos(np.dot(v, [0, 0, 1]))

    # Handling the special case where the vectors are parallel/anti-parallel
    if np.isclose(np.linalg.norm(axis), 0):
        if v[2] > 0:
            return np.eye(3)
        else:
            return np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
    else:
        axis /= np.linalg.norm(axis)

    # Rodrigues' rotation formula
    K = skew_symmetric(axis)
    R = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * np.dot(K, K)
    return R
