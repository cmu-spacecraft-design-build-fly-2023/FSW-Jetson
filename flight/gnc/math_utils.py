import numpy as np
from scipy.linalg import expm, cholesky


def dcm_from_q(q):
    norm = np.linalg.norm(q)
    q0, q1, q2, q3 = q / norm if norm != 0 else q

    # DCM
    Q = np.array([
        [2 * q1**2 + 2 * q0**2 - 1, 2 * (q1 * q2 - q3 * q0), 2 * (q1 * q3 + q2 * q0)],
        [2 * (q1 * q2 + q3 * q0), 2 * q2**2 + 2 * q0**2 - 1, 2 * (q2 * q3 - q1 * q0)],
        [2 * (q1 * q3 - q2 * q0), 2 * (q2 * q3 + q1 * q0), 2 * q3**2 + 2 * q0**2 - 1]
    ])

    return Q


def rotm2quat(r):
    q = np.zeros(4)
    q[0] = 0.5 * np.sqrt(1 + r[0, 0] + r[1, 1] + r[2, 2])
    q[1] = (1 / (4 * q[0])) * (r[2][1] - r[1][2])
    q[2] = (1 / (4 * q[0])) * (r[0][2] - r[2][0])
    q[3] = (1 / (4 * q[0])) * (r[1][0] - r[0][1])
    return np.array(q)


def geodesic_distance(q1, q2):
    return 1 - abs(np.dot(q1, q2))


def random_rotation_matrix(P, Q0=np.diag(np.ones(3))):
    Δ = cholesky(P, lower=True)
    ϕ = Δ @ np.random.randn(3, 1)
    rot = Q0 @ expm(skew_symmetric(ϕ))
    return rot


def L(q):
    """
    Left-multiply
    """
    L = np.zeros((4, 4))
    L[0, 0] = q[0]
    L[0, 1:] = -q[1:]
    L[1:, 0] = q[1:]
    L[1:, 1:] = q[0] * np.identity(3) + skew_symmetric(q[1:])
    return L


def R(q):
    """
    Right-multiply
    """
    R = np.zeros((4, 4))
    R[0, 0] = q[0]
    R[0, 1:] = -q[1:]
    R[1:, 0] = q[1:]
    R[1:, 1:] = q[0] * np.identity(3) - skew_symmetric(q[1:])
    return R


def conj(q):
    """
    Inverse of a unit quaternion is its conjugate, i.e. same quaternion with a negated vector part
    """
    qr = np.zeros(4)
    qr[0] = q[0]
    qr[1:] = -q[1:]
    return qr


def skew_symmetric(w):
    """
    Returns the skew symmetric form of a numpy array.
    w --> [w]
    """

    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])
