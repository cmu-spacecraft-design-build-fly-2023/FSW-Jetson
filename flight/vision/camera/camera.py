import numpy as np
import cv2
import yaml
from landmarks.CoordinateConverter import CoordinateConverter

class Camera:

    def __init__(self, id):
        self.id = id
        self.camera_matrix = None
        self.distortion_coefficients = None
        self.cap = None

    def connect_to_camera(self):
        # Connect to the camera with the specified ID
        try:
            self.cap = cv2.VideoCapture(self.id)
        except Exception as e:
            print("Error in connecting to camera")
        # TODO error handling

    def disconnect_from_camera(self):
        # Disconnect from the camera
        if self.cap is not None:
            self.cap.release()

    def calibrate(self):
        pass

    def load_camera_parameters(self, cam_file):
        # Load camera parameters from an XML file
        try:
            with open(cam_file, 'r') as file:
                config = yaml.safe_load(file)
                self.camera_matrix = np.array(config['camera_parameters']['intrinsic_matrix']).reshape(3,3)
                self.distortion_coefficients = np.array(config['camera_parameters']['distortion_coefficients'])
        except Exception as e:
            print("error loading from param file")
            self.calibrate()

        
    def apply_inverse_intrinsics(self, points):
        # Apply inverse intrinsic transformation to points in pixel coordinates
        # if self.camera_matrix is not None:
        #     inv_camera_matrix = np.linalg.inv(self.camera_matrix)
        #     return cv2.undistortPoints(points, self.camera_matrix, self.distortion_coefficients, R=inv_camera_matrix)
        # else:
        #     raise ValueError("Camera parameters not loaded or calibrated.")
        depth = 1.0
        normalized_coords = cv2.undistortPoints(points, self.camera_matrix, self.distortion_coefficients)
        normalized_coords_with_depth = np.concatenate((normalized_coords[0], depth * np.ones((1, 1), dtype=np.float32)), axis=1)
        self.camera_coords = np.dot(np.linalg.inv(self.camera_matrix), normalized_coords_with_depth.T).T
        self.camera_vector = self.camera_coords / np.linalg.norm(self.camera_coords)
        print(self.camera_coords)



    def capture_image(self):
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                # Undistort the captured image using the loaded camera parameters
                if self.camera_matrix is not None and self.distortion_coefficients is not None:
                    undistorted_image = cv2.undistort(frame, self.camera_matrix, self.distortion_coefficients)
                    return undistorted_image
                else:
                    return frame  # Return the original image if parameters are not available
            else:
                return None
        else:
            raise ValueError("Camera not connected. Call connect_to_camera() first.")

if __name__ == "__main__":
    cam = Camera(0)
    # verify live feed 
    cam.connect_to_camera()

    # load camera params
    cam.load_camera_parameters('cam_params.yml')

    # capture image and run ML pipline
    # TODO  

    # find camera coordinates 
    cam.apply_inverse_intrinsics(np.array([[640, 32]], dtype=np.float32))

    # ECEF 
    converter = CoordinateConverter()
    converter.lla_to_eci('landmarks/17R_outboxes.csv', 'landmarks/eci_coordinates.csv')

    # from labels retrieve lat long and corresponding ECEF, convert to ECI 

