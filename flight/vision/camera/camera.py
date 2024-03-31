import cv2
import os
import yaml
import time
from datetime import datetime
import logging
from typing import List


logging.basicConfig(filename='camera_errors.log', level=logging.ERROR,
                    format='%(asctime)s - Camera %(name)s - %(levelname)s - %(message)s')

class CameraErrorCodes:
    CAMERA_INITIALIZATION_FAILED = 1001
    CAPTURE_FAILED = 1002
    NO_IMAGES_FOUND = 1003
    READ_FRAME_ERROR = 1004
    CAMERA_NOT_OPERATIONAL = 1005
    CONFIGURATION_ERROR = 1006

error_messages = {
    CameraErrorCodes.CAMERA_INITIALIZATION_FAILED: "Camera initialization failed.",
    CameraErrorCodes.CAPTURE_FAILED: "Failed to capture image.",
    CameraErrorCodes.NO_IMAGES_FOUND: "No images found.",
    CameraErrorCodes.READ_FRAME_ERROR: "Error reading frame.",
    CameraErrorCodes.CAMERA_NOT_OPERATIONAL: "Camera is not operational.",
    CameraErrorCodes.CONFIGURATION_ERROR: "Configuration error."
}


class Camera:
    def __init__(self, camera_id):
        try:
            config = self.load_config('../../../configuration/camera_configuration.yml')
        except Exception as e:
            logging.error(f"{error_messages[CameraErrorCodes.CONFIGURATION_ERROR]}: {e}")
            raise ValueError(error_messages[CameraErrorCodes.CONFIGURATION_ERROR])
            
        self.camera_id = camera_id
        os.makedirs(self.image_folder, exist_ok=True)
        self.max_startup_time = config['camera']['max_startup_time'] 
        self.camera_status = self.initialize_camera()
        self.camera_settings = config['camera']['cameras'].get(str(camera_id), {})
        self.resolution = (self.camera_settings['resolution']['width'], self.camera_settings['resolution']['height'])       
        self.image_folder = f"captured_images/camera_{camera_id}"
        self.zoom = self.camera_settings.get('zoom')
        self.focus = self.camera_settings.get('focus')
        self.exposure = self.camera_settings.get('exposure')

    def load_config(config_path):
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
        if hasattr(self, 'cap') and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                self.cap.release()
                self.camera_status = 0

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
            cap = cv2.VideoCapture(self.camera_id)
            ret, frame = cap.read()
            if ret:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                image_name = f"{self.image_folder}/{timestamp}.jpg"
                cv2.imwrite(image_name, frame)
                print(f"Image captured from camera {self.camera_id} at {timestamp}")
            else:
                print(f"Failed to capture image from camera {self.camera_id}")
                self.log_error(CameraErrorCodes.READ_FRAME_ERROR)
                self.log_error(CameraErrorCodes.CAPTURE_FAILED)
                self.camera_status = 0
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
            cap = cv2.VideoCapture(self.camera_id)
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    cv2.imshow(f"Live Feed from Camera {self.camera_id}", frame)
                else:
                    print(f"Error reading frame from camera {self.camera_id}")
                    self.log_error(CameraErrorCodes.READ_FRAME_ERROR)

                    break
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cap.release()
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
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_EXPOSURE, self.exposure)


class CameraManager:

    def __init__(self):
        pass

    def get_available_frames(self):
        pass
    
    def return_status(self):
        pass


    def turn_on_cameras(self) -> List[bool]:
        pass

    def turn_off_cameras(self) -> List[bool]:
        pass

    # Debuf and FDIR
    def get_camera(self, camera_id: int) -> Camera:
        pass