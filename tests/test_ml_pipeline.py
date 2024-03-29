import cv2
import numpy as np
from PIL import Image
from flight.vision.rc import RegionClassifier
from flight.vision import MLPipeline
from fake_camera_feed import FakeCameraFeed

if __name__ == "__main__":
    camera_feed = FakeCameraFeed()
    frames_with_ids = list(camera_feed.get_frames())

    pipeline = MLPipeline()
    pipeline.run_ml_pipeline(frames_with_ids)