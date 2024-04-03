import cv2
import os
import yaml
import time
from datetime import datetime
import logging
from typing import List
import numpy as np


logging.basicConfig(filename='camera_errors.log', level=logging.ERROR,
                    format='%(asctime)s - Camera %(name)s - %(levelname)s - %(message)s')

class CameraErrorCodes:
    CAMERA_INITIALIZATION_FAILED = 1001
    CAPTURE_FAILED = 1002
    NO_IMAGES_FOUND = 1003
    READ_FRAME_ERROR = 1004
    CAMERA_NOT_OPERATIONAL = 1005
    CONFIGURATION_ERROR = 1006
    SUN_BLIND = 1007

error_messages = {
    CameraErrorCodes.CAMERA_INITIALIZATION_FAILED: "Camera initialization failed.",
    CameraErrorCodes.CAPTURE_FAILED: "Failed to capture image.",
    CameraErrorCodes.NO_IMAGES_FOUND: "No images found.",
    CameraErrorCodes.READ_FRAME_ERROR: "Error reading frame.",
    CameraErrorCodes.SUN_BLIND: "Image blinded by the sun",
    CameraErrorCodes.CAMERA_NOT_OPERATIONAL: "Camera is not operational.",
    CameraErrorCodes.CONFIGURATION_ERROR: "Configuration error."
}

class Frame:
    def __init__(self, frame, camera_id, timestamp):
        self.camera_id = camera_id
        self.frame = frame
        self.timestamp = timestamp

    def save(self):
        pass

class Camera:
    def __init__(self, camera_id, config_path):
        try:
            config = self.load_config(config_path)
        except Exception as e:
            logging.error(f"{error_messages[CameraErrorCodes.CONFIGURATION_ERROR]}: {e}")
            raise ValueError(error_messages[CameraErrorCodes.CONFIGURATION_ERROR])

        self.camera_id = camera_id
        self.image_folder = f"captured_images/camera_{camera_id}"
        os.makedirs(self.image_folder, exist_ok=True)
        self.max_startup_time = config['max_startup_time'] 
        self.camera_settings = config['cameras'].get(camera_id, {})
        self.resolution = (self.camera_settings['resolution']['width'], self.camera_settings['resolution']['height'])     
        self.zoom = self.camera_settings.get('zoom')
        self.focus = self.camera_settings.get('focus')
        self.exposure = self.camera_settings.get('exposure')
        self.camera_status = self.initialize_camera()
        self._current_frame = None

    def load_config(self,config_path):
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)

    def log_error(self, error_code):
        message = error_messages.get(error_code, "Unknown error.")
        logging.error(f"Camera {self.camera_id}: {message}")


    def initialize_camera(self):
        start_time = time.time()
        cap = cv2.VideoCapture(self.camera_id)
        if cap.isOpened():
            elapsed_time = (time.time() - start_time) * 1000  # Calculate elapsed time in milliseconds
            if elapsed_time <= self.max_startup_time:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
                return 1
            else:
                print(f"Camera {self.camera_id} initialization exceeded {self.max_startup_time} milliseconds.")
                self.log_error(CameraErrorCodes.CAMERA_INITIALIZATION_FAILED)
                return 0
        else:
            return 0

    def check_operational_status(self):
        if not hasattr(self, 'cap') or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_id)
            if self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
                self.camera_status = 1
                return self.camera_status
            else:
                self.camera_status = 0
                return self.camera_status
        return self.camera_status  
    
    
    def capture_image(self):
        if self.check_operational_status():
            # cap = cv2.VideoCapture(self.camera_id)
            try:
                ret, frame = self.cap.read()
                if ret:
                    if not self.is_blinded_by_sun(frame):
                        timestamp = datetime.now()
                        print(f"Image captured from camera {self.camera_id} at {timestamp}")
                        self.current_frame = Frame(frame,self.camera_id,timestamp)
                    else:
                        print(f"blinded by the lights")
                        self.log_error(CameraErrorCodes.SUN_BLIND)
                else:
                    print(f"Failed to capture image from camera {self.camera_id}")
                    self.log_error(CameraErrorCodes.READ_FRAME_ERROR)
                    self.log_error(CameraErrorCodes.CAPTURE_FAILED)
                    self.camera_status = 0
            finally:
                self.cap.release()
        else:
            print(f"Camera {self.camera_id} is not operational.")
            self.log_error(CameraErrorCodes.CAMERA_NOT_OPERATIONAL)
        return self.camera_status

    @property
    def current_frame(self):
        return self._current_frame
    
    @current_frame.setter
    def current_frame(self, value):
        self._current_frame = value


    def read_image_from_path(self):
        image_files = os.listdir(self.image_folder)
        if not image_files:
            print(f"No images found for camera {self.camera_id}")
            self.log_error(CameraErrorCodes.NO_IMAGES_FOUND)
            return None
        latest_image_path = max([os.path.join(self.image_folder, filename) for filename in image_files], key=os.path.getctime)
        return cv2.imread(latest_image_path)

    def set_zoom(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_ZOOM, self.zoom)

    def set_focus(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FOCUS, self.focus)

    def set_exposure(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
    
    def is_blinded_by_sun(self, image):
        """gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresholded = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)
        # Calculate the percentage of bright pixels
        bright_pixels = cv2.countNonZero(thresholded)
        total_pixels = image.shape[0] * image.shape[1]
        bright_ratio = bright_pixels / total_pixels
        if bright_ratio > 0.5:  
            return True """
        return False
    

    # DEBUG only 
    def get_live_feed(self):
        if self.check_operational_status():
            cv2.namedWindow(f"Live Feed from Camera {self.camera_id}")
            # cap = cv2.VideoCapture(self.camera_id)
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    cv2.imshow(f"Live Feed from Camera {self.camera_id}", frame)
                else:
                    print(f"Error reading frame from camera {self.camera_id}")
                    self.log_error(CameraErrorCodes.READ_FRAME_ERROR)

                    break
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            self.cap.release()
            cv2.destroyAllWindows()
        else:
            print(f"Camera {self.camera_id} is not operational.")
            self.log_error(CameraErrorCodes.CAMERA_NOT_OPERATIONAL)
        return self.camera_status
    



class CameraManager:

    def __init__(self, camera_ids, config_path="configuration/camera_configuration.yml"):
        self.cameras = {camera_id: Camera(camera_id, config_path=config_path) for camera_id in camera_ids}
        number_of_cameras = len(self.cameras)
        self.camera_frames = []

    def capture_images(self):
        """
        capture stores images for all cameras given in the list
        """
        for camera_id, camera in self.cameras.items():
            camera.capture_image()
    
    def turn_on_cameras(self):
        """
        re-initialises cameras
        Returns:
            Bool status list of camera  
        """
        status_list = []
        for camera_id, camera in self.cameras.items():
            status = camera.initialize_camera()
            status_list.append(status == 1)
        return status_list


    def turn_off_cameras(self,camera_ids: List[int]):
        """
       Release cameras of given IDs 
        """
        for camera_id in camera_ids:
            camera = self.cameras.get(camera_id)
            if camera is not None and hasattr(camera, 'cap') and camera.cap.isOpened():
                camera.cap.release()
                print(f"Camera {camera_id} turned off.")

    def get_camera(self, camera_id: int) -> Camera:
        """
       takes in camera ID 
       Returns:
           camera object of specified ID  
        """
        return self.cameras.get(camera_id)   

    def get_available_frames(self):
        """
        Get all available image frames for each camera.
        Returns:
            A dictionary with camera IDs as keys and lists of image paths as values.
        """
        camera_frames = []
        for camera_id, camera in self.cameras.items():
            try:
                camera_frames.append(camera.current_frame)
            except:
                print(f"No frames found for camera {camera_id}, or no images are present.")
                camera.log_error(CameraErrorCodes.NO_IMAGES_FOUND)
        return camera_frames
    
    # def return_status(self):
    #     pass


    @classmethod
    def show(self, frame: Frame):
        cv2.imshow(f"Camera {frame.camera_id} Frame at {frame.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", frame.frame)

    @classmethod
    def close_windows(self):
        cv2.destroyAllWindows()


