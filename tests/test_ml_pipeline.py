"""
Main Execution Script for ML Pipeline with Fake Camera Feed

This script demonstrates the integration and usage of a machine learning pipeline for region classification and landmark detection using a simulated camera feed. It utilizes the FakeCameraFeed class to generate virtual camera frames and processes them through the MLPipeline to classify geographic regions and detect landmarks within those regions. This example serves as a testbed for verifying the functionality and performance of the vision components in a controlled environment without the need for physical camera inputs.

Author: Eddie
Date: [Creation or Last Update Date]
"""

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
