"""
Main Execution Script for ML Pipeline with Fake Camera Feed

This script demonstrates the integration and usage of a machine learning pipeline for region classification and landmark detection using a simulated camera feed. It utilizes the FakeCameraFeed class to generate virtual camera frames and processes them through the MLPipeline to classify geographic regions and detect landmarks within those regions. This example serves as a testbed for verifying the functionality and performance of the vision components in a controlled environment without the need for physical camera inputs.

Requirement:
    Set the PYTHONPATH environment variable to include the root of project to make the package flight discoverable.
    export PYTHONPATH="/path/to/project_root:$PYTHONPATH"

Author: Eddie
Date: [Creation or Last Update Date]
"""

import cv2
import numpy as np
from PIL import Image
from collections import Counter

from flight.vision.rc import RegionClassifier
from flight.vision import MLPipeline, FrameProcessor
from fake_camera_feed import FakeCameraFeed

def print_ml_frames(ml_frames):
    # Counting using Counter from the collections module
    camera_ids = [camera_id for _, camera_id in ml_frames]
    camera_counts = Counter(camera_ids)
    
    for camera_id, count in camera_counts.items():
        print(f"Camera ID {camera_id} has {count} images processed for ML pipeline.")

def print_pipeline_results(results):
    """
    Prints the results from the ML pipeline batch processing.
    
    Args:
        results (list of tuples): Each tuple contains a camera ID and a list of tuples,
                                  each of which contains a region ID and a LandmarkDetectionResult object.
    """
    for camera_id, regions_and_landmarks in results:
        for region, detection_result in regions_and_landmarks:
            centroid_xy = detection_result.centroid_xy
            centroid_latlons = detection_result.centroid_latlons
            landmark_classes = detection_result.landmark_classes
            print(f"Camera {camera_id}: Region {region} Landmarks: {centroid_xy}, {centroid_latlons}, {landmark_classes}")

if __name__ == "__main__":
    camera_feed = FakeCameraFeed()
    frames_with_ids = list(camera_feed.get_frames())
    processor = FrameProcessor()
    pipeline = MLPipeline()
    ml_frames = processor.process_for_ml_pipeline(frames_with_ids)
    result = pipeline.run_ml_pipeline_on_batch(ml_frames)

    print_ml_frames(ml_frames)
    print_pipeline_results(result)