import cv2
import os
import yaml
import time
from datetime import datetime

class Camera:
    def __init__(self, camera_id, resolution=(1280, 720)):
        config = self.load_config('../../../configuration/camera_configuration.yml')
        self.camera_id = camera_id
        self.resolution = resolution
        self.image_folder = f"captured_images/camera_{camera_id}"
        os.makedirs(self.image_folder, exist_ok=True)
        self.max_startup_time = config['camera']['max_startup_time'] 
        self.camera_status = self.initialize_camera()

    def load_config(config_path):
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)

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
        else:
            print(f"Camera {self.camera_id} is not operational.")

    def get_latest_image(self):
        image_files = os.listdir(self.image_folder)
        if not image_files:
            print(f"No images found for camera {self.camera_id}")
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
                    break
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            cap.release()
            cv2.destroyAllWindows()
        else:
            print(f"Camera {self.camera_id} is not operational.")