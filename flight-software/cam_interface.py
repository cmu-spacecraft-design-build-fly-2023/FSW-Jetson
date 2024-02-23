import cv2
import os
from datetime import datetime

class Camera:
    def __init__(self, camera_id, resolution=(1280, 720)):
        self.camera_id = camera_id
        self.resolution = resolution
        self.image_folder = f"captured_images/camera_{camera_id}"
        os.makedirs(self.image_folder, exist_ok=True)
        self.camera_status = self.initialize_camera()

    def initialize_camera(self):
        cap = cv2.VideoCapture(self.camera_id)
        if cap.isOpened():
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            return 1
        else:
            return 0

    def capture_image(self):
        cap = cv2.VideoCapture(self.camera_id)
        ret, frame = cap.read()
        if ret:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            image_name = f"{self.image_folder}/{timestamp}.jpg"
            cv2.imwrite(image_name, frame)
            print(f"Image captured from camera {self.camera_id} at {timestamp}")
        else:
            print(f"Failed to capture image from camera {self.camera_id}")

    def get_latest_image(self):
        image_files = os.listdir(self.image_folder)
        if not image_files:
            print(f"No images found for camera {self.camera_id}")
            return None
        latest_image_path = max([os.path.join(self.image_folder, filename) for filename in image_files], key=os.path.getctime)
        return cv2.imread(latest_image_path)

    def get_live_feed(self):
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
