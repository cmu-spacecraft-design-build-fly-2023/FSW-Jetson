"""
Requirement:
    Set the PYTHONPATH environment variable to include the root of project to make the package flight discoverable.
    export PYTHONPATH="/path/to/project_root:$PYTHONPATH"

    export SPACECRAFT_ROOT="/path/to/project_root"
"""

# import necessary modules
from PIL import Image
import cv2
import numpy as np
from flight.vision.rc import RegionClassifier
from flight.vision.ld import LandmarkDetector
from tests.fake_camera_feed import FakeCameraFeed

class MLPipeline:
    def __init__(self):
        # Initialize the classifier here if it has any global setup.
        self.region_classifier = RegionClassifier()
        pass

    def is_frame_dark(self, frame, threshold=0.5):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        dark_percentage = np.sum(gray_frame < 60) / np.prod(gray_frame.shape)
        return dark_percentage > threshold

    def classify_frame(self, frame):
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        # Use self.classifier if it's initialized in __init__
        predicted_list = self.region_classifier.classify_region_ids(frame_pil)
        return predicted_list

    def run_ml_pipeline(self, frames_with_ids):
        for frame, camera_id in frames_with_ids:
            if not self.is_frame_dark(frame):
                pred_regions = self.classify_frame(frame)
                print(f"Camera ID {camera_id} detected regions:", pred_regions)
                for region in pred_regions:
                    detector = LandmarkDetector(region_id=region)
                    centroid_xy, centroid_latlons, landmark_classes = detector.detect_landmarks(frame)
                    print(f"    Region {region} Landmarks: {centroid_xy}, {centroid_latlons}, {landmark_classes}")
                
            else:
                print(f"Camera ID {camera_id}: Frame is too dark and was skipped.")