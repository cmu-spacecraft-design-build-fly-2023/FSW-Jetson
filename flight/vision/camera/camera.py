import cv2
import os
import yaml
import time
from datetime import datetime
import logging
from typing import List
import numpy as np
import subprocess


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

class ImageData:
    def __init__(self, camera_id, frame, timestamp):
        self.camera_id = camera_id
        self.frame = frame
        self.timestamp = timestamp


class Camera:
    def __init__(self, camera_id):
        try:
            config = self.load_config('../../../configuration/camera_configuration.yml')
        except Exception as e:
            logging.error(f"{error_messages[CameraErrorCodes.CONFIGURATION_ERROR]}: {e}")
            raise ValueError(error_messages[CameraErrorCodes.CONFIGURATION_ERROR])
            
        self.camera_id = camera_id
        self.image_folder = f"captured_images/camera_{camera_id}"
        os.makedirs(self.image_folder, exist_ok=True)
        self.max_startup_time = config['camera']['max_startup_time'] 
        self.camera_settings = config['camera']['cameras'].get(camera_id, {})
        self.resolution = (self.camera_settings['resolution']['width'], self.camera_settings['resolution']['height'])     
        self.zoom = self.camera_settings.get('zoom')
        self.focus = self.camera_settings.get('focus')
        self.exposure = self.camera_settings.get('exposure')
        self.camera_status = self.initialize_camera()
        self.image_data = [] # store camera frame  

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
        # if hasattr(self, 'cap') and self.cap.isOpened():
        #     ret, frame = self.cap.read()
        #     print("inside this")
        #     if not ret:
        #         self.cap.release()
        #         self.camera_status = 0

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
                        exposure_value = f"v4l2-ctl -d /dev/video{self.camera_id} --get-ctrl exposure_absolute"
                        subprocess.run(exposure_value, shell=True, check=True)

                        timestamp = datetime.now()
                        image_name = f"{self.image_folder}/{timestamp}.jpg"
                        cv2.imwrite(image_name, frame)
                        print(f"Image captured from camera {self.camera_id} at {timestamp}")
                        self.image_data.append(ImageData(self.camera_id,frame,timestamp))
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

    def get_latest_image(self):
        image_files = os.listdir(self.image_folder)
        if not image_files:
            print(f"No images found for camera {self.camera_id}")
            self.log_error(CameraErrorCodes.NO_IMAGES_FOUND)
            return None
        latest_image_path = max([os.path.join(self.image_folder, filename) for filename in image_files], key=os.path.getctime)
        return cv2.imread(latest_image_path)

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
    
    def set_zoom(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_ZOOM, self.zoom)

    def set_focus(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FOCUS, self.focus)

    def set_exposure(self):
        # if hasattr(self, 'cap') and self.cap.isOpened():
        #     self.cap.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
        try:
            # disable auto mode 
            disable_auto_exposure_command = f"v4l2-ctl -d /dev/video{self.camera_id} --set-ctrl exposure_auto=1"
            subprocess.run(disable_auto_exposure_command, shell=True, check=True)

            command = f"v4l2-ctl -d /dev/video{self.camera_id} --set-ctrl exposure_absolute={self.exposure}"
            subprocess.run(command, shell=True, check=True)
            print(f"Exposure set to {self.exposure} for camera {self.camera_id}.")

        except subprocess.CalledProcessError as e:
            print(f"Failed to set exposure for camera {self.camera_id}: {e}")
            self.log_error(CameraErrorCodes.CONFIGURATION_ERROR)

    def enable_default_exposure(self):
        command = f"v4l2-ctl -d /dev/video{self.camera_id} --set-ctrl exposure_absolute={1}"
        subprocess.run(command, shell=True, check=True)

        # enable_auto_exposure_command = f"v4l2-ctl -d /dev/video{self.camera_id} --set-ctrl exposure_auto=3"
        # subprocess.run(enable_auto_exposure_command, shell=True, check=True)


    
    def is_blinded_by_sun(self, image):

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresholded = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)
        
        # Calculate the percentage of bright pixels
        bright_pixels = cv2.countNonZero(thresholded)
        total_pixels = image.shape[0] * image.shape[1]
        bright_ratio = bright_pixels / total_pixels
        if bright_ratio > 0.5:  
            return True 
        return False


class CameraManager:

    def __init__(self, camera_ids):
        self.cameras = {camera_id: Camera(camera_id) for camera_id in camera_ids}
        number_of_cameras = 6
        self.camera_frames = np.zeros([number_of_cameras,3])
    
    def capture_images(self):
        """
       capture stores images for all cameras given in the list
        """
        for camera_id, camera in self.cameras.items():
            camera.capture_image()
    
    def set_exposure(self):
        for camera_id, camera in self.cameras.items():
            camera.set_exposure()
    
    def enable_default_exposure(self):
        for camera_id, camera in self.cameras.items():
            camera.enable_default_exposure()


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
        camera_frames = {}
        for camera_id, camera in self.cameras.items():
            image_folder = camera.image_folder
            try:
                # image_files = [os.path.join(image_folder, filename) for filename in os.listdir(image_folder)]
                # sorted_image_files = sorted(image_files, key=os.path.getctime)
                camera_frames[camera_id] = camera.image_data
            except:
                print(f"No frames found for camera {camera_id}, or no images are present.")
                camera.log_error(CameraErrorCodes.NO_IMAGES_FOUND)
                camera_frames[camera_id] = []  # No images found for this camera
        return camera_frames
    
    # def return_status(self):
    #     pass

    def turn_off_cameras(self,camera_ids: List[int]):
        """
       Release cameras of given IDs 
        """
        for camera_id in camera_ids:
            camera = self.cameras.get(camera_id)
            if camera is not None and hasattr(camera, 'cap') and camera.cap.isOpened():
                camera.cap.release()
                print(f"Camera {camera_id} turned off.")




# Example
camera_ids = [0] 
manager = CameraManager(camera_ids)

# Capture images from all cameras
manager.capture_images()
manager.set_exposure()
manager.capture_images()  
manager.enable_default_exposure()
manager.capture_images()

all = manager.get_available_frames()
# imgdata = all
# for i in camera_ids:
#     imgd = all[i][0]
#     print(imgd.timestamp.strftime('%Y-%m-%d %H:%M:%S'))
    

# cv2.imshow(f"Camera {imgdata.camera_id} Frame at {imgdata.timestamp.strftime('%Y-%m-%d %H:%M:%S')}", imgdata.frame)
# cv2.waitKey(0) 
# cv2.destroyAllWindows()
