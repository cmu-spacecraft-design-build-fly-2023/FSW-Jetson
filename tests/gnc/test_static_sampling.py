
import numpy as np
from flight.gnc import sampling, triangulation
from flight.gnc.utils import *


camera_body_frames = {
    # ID 1: Top X-axis (Positive X-direction)
    1: np.array([1.0, 0.0, 0.0]),
    # ID 2: Top Y-axis (Positive Y-direction)
    2: np.array([0.0, 1.0, 0.0]),
    # ID 3: Top Z-axis (Positive Z-direction)
    3: np.array([0.0, 0.0, 1.0]),
    # ID 4: Bottom X-axis (Negative X-direction)
    4: np.array([-1.0, 0.0, 0.0]),
    # ID 5: Bottom Y-axis (Negative Y-direction)
    5: np.array([0.0, -1.0, 0.0]),
    # ID 6: Bottom Z-axis (Negative Z-direction)
    6: np.array([0.0, 0.0, -1.0])
}


def find_camera_ID(camera_body_frames, gt_attitude_q, landmarks):
    """
    Find the camera ID most likely to have taken the picture based on the ECI position of the landmarks
    """
    # Get camera frame vectors in body
    top_x_body = camera_body_frames[1]
    top_y_body = camera_body_frames[2]
    top_z_body = camera_body_frames[3]
    bottom_x_body = camera_body_frames[4]
    bottom_y_body = camera_body_frames[5]
    bottom_z_body = camera_body_frames[6]

    cam_vec_body = [top_x_body, top_y_body, top_z_body, bottom_x_body, bottom_y_body, bottom_z_body] # All unit vectors

    # Mean landmark body frame position
    mean_landmark_body = dcm_from_q(gt_attitude_q).T @ np.mean(landmarks, axis=0)

    cam_to_ld_dir = np.zeros((6, 3))
    for i in range(6):
        cam_to_ld_dir[i, :] = (cam_vec_body[i] - mean_landmark_body) / np.linalg.norm(cam_vec_body[i] - mean_landmark_body)

    angcos = [
        np.dot(cam_to_ld_dir[0, :], top_x_body),
        np.dot(cam_to_ld_dir[1, :], top_y_body),
        np.dot(cam_to_ld_dir[2, :], top_z_body),
        np.dot(cam_to_ld_dir[3, :], bottom_x_body),
        np.dot(cam_to_ld_dir[4, :], bottom_y_body),
        np.dot(cam_to_ld_dir[5, :], bottom_z_body)
    ]

    # Get camera ID
    camera_ID = np.argmax(angcos) + 1

    return camera_ID

if __name__ == "__main__":

    from time import sleep 

    # Load landmarks from CSV file
    landmarks = np.loadtxt("tests/gnc/data/4/landmarks.csv", delimiter=',')
    # Load measurements from CSV file
    measurements = np.loadtxt("tests/gnc/data/4/measurements.csv", delimiter=',')
    # Load ground truth orbit position and attitude quaternion from CSV file
    gt_data = np.loadtxt("tests/gnc/data/4/gt.csv", delimiter=',', dtype=np.float64)
    gt_orbit_pos = gt_data[0:3]
    gt_attitude_q = gt_data[3:7]

    """import plotter
    Qs = sampling.sample_attitude_hemisphere(np.array([0, 0, -1]), ang_step=np.deg2rad(20))
    ut = np.array([0.0, 0, -1])
    vv = np.zeros((Qs.shape[0], 3))
    for i in range(Qs.shape[0]):
        vv[i, :] = Qs[i, :, :] @ ut
    plotter.scatter3D(vv, equal=True)"""

    
    # Initial orbit position guess by using the landmarks
    r0 = sampling.sample_sso_orbit_pos_near_landmark(landmarks)
    #Initial attitude guess by using the camera ID and nadir vector using the initial orbit guess
    n0 = triangulation.compute_nadir_vector(r0)
    cam_ID = find_camera_ID(camera_body_frames, gt_attitude_q, landmarks) # For flight version, we will know which camera took the picture (so no gt attitude)
    print(cam_ID)
    
    q0 = triangulation.nadir_pointing_attitude(camera_body_frames[cam_ID], n0)
    Q0 = dcm_from_q(q0)
 

    # Need to fix - some divergence with Julia version
    rf, Qf, cost = triangulation.sampling_search(landmarks, measurements, Q0, camera_body_frames[cam_ID], N_samples=100, initial_angular_sampling_step=np.deg2rad(180), decay=0.95, max_iterations=100, verbose=True)

    print("Estimated orbit position: ", rf)
    print("Estimated attitude: ", Qf)
    print("Cost: ", cost)

    norm_rf_gt_orbit_pos = np.linalg.norm(rf - gt_orbit_pos)
    print("Norm(rr - gt_orbit_pos):", norm_rf_gt_orbit_pos)
    gt_attitude_Q = dcm_from_q(gt_attitude_q)
    dR = gt_attitude_Q.T @ Qf
    angle_err = np.rad2deg(np.arccos((np.trace(dR) - 1) / 2))
    print("Angular Error (deg):", angle_err)


