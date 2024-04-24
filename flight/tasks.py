"""
Payload Task List

Description: It contains the high-level tasks/activities processed by the payload.

Author: Ibrahima S. Sow
Date: [Creation or Last Update Date]
"""

from flight.logger import Logger
from flight.demo_frames import demo_frames # Function to provide frames insequence
from flight.vision import MLPipeline
from flight.vision.camera import Frame
import os
import cv2
import datetime
from pathlib import Path


# TODO - fill in functions
# TODO - Fill in the functions with the correct parameters and return types


# DEBUG
import random


def debug_hello(payload):
    Logger.log("INFO", "Hello from the payload!")


def debug_random_error(payload):
    if random.random() < 0.7:
        raise Exception("Random error occurred!")


def debug_goodbye(payload):
    print("Goodbye from the payload!")


def debug_number(payload):
    print(f"Processing {payload} to {payload*random.random()}")


# Time


def synchronize_time(payload):
    """Synchronize the time."""
    pass


def request_time(payload):
    """Request the time."""
    pass


# Payload Control


def request_payload_state(payload):
    """Request the current state of the payload."""
    


def request_payload_monitoring_data(payload):
    """Request the monitoring data of the payload."""
    pass


def restart_payload(payload):
    """Restart the payload."""
    pass


def request_logs_from_last_x_seconds(payload):
    """Request the logs from the last X seconds."""
    pass


def delete_all_logs(payload):
    """Delete all logs."""
    pass


# Camera


def capture_and_send_image(payload):
    """Capture and send an image."""
    pass


def request_last_image(payload):
    """Request the last image."""
    pass


def request_image_metadata(payload):
    """Request the metadata of an image."""
    pass


def turn_on_cameras(payload):
    """Turn on the cameras."""
    pass


def turn_off_cameras(payload):
    """Turn off the cameras."""
    pass


def request_image_storage_info(payload):
    """Request the storage information of the images."""
    pass


def change_camera_resolution(payload):
    """Change the resolution of the camera."""
    pass


def delete_all_stored_images(payload):
    """Delete all stored images."""
    pass


def enable_camera_x(payload):
    """Enable camera X."""
    pass


def disable_camera_x(payload):
    """Disable camera X."""
    pass


def request_camera_status(payload):
    """Request the status of the camera."""
    pass


# Inference

def run_ml_pipeline(payload):
    """
    Function to run ML pipeline on the latest frame retrieved from a cycling list of images.
    """
    pipeline = MLPipeline()
    latest_frame = demo_frames.get_latest_frame()
    if latest_frame is not None:
        regions_and_landmarks = pipeline.run_ml_pipeline_on_single(latest_frame)
        if regions_and_landmarks is not None:
            pipeline.visualize_landmarks(latest_frame, regions_and_landmarks, "data/inference_output")
    #else:
    #    print("No frame available to process.")

def request_landmarked_image(payload):
    """Request a landmarked image and return a Frame object containing the image and its metadata."""
    image_dir = "data/inference_output"
    image_path = os.path.join(image_dir, "frame_w_landmarks.jpg")
    metadata_path = os.path.join(image_dir, "frame_metadata.txt")

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        Logger.log("ERROR", "The landmarked image file was not found.")
        return None

    # Load and parse the metadata
    if not os.path.exists(metadata_path):
        Logger.log("ERROR", "The metadata file was not found.")
        return None
    
    metadata = {}
    with open(metadata_path, 'r') as f:
        for line in f:
            key, value = line.strip().split(': ')
            metadata[key] = value

    # Extract metadata information
    camera_id = int(metadata["Camera ID"])
    timestamp = datetime.datetime.strptime(metadata["Timestamp"], "%Y-%m-%d %H:%M:%S.%f")
    frame_id = metadata["Frame ID"]

    # Create a Frame object
    frame = Frame(frame=image, camera_id=camera_id, timestamp=timestamp)
    Logger.log("INFO", f"got the frame {frame}")
    return frame


def enable_region_x(payload):
    """Enable region X."""
    pass


def disable_region_x(payload):
    """Disable region X."""
    pass


def request_landmarked_image_metadata(payload):
    """Request the metadata of a landmarked image."""
    pass


def request_region_x_status(payload):
    """Request the status of region X."""
    pass


# Attitude and Orbit Estimation


def reset_aod_state(payload):
    """Reset the attitude and orbit estimation state."""
    pass


def request_aod_last_estimate(payload):
    """Request the last estimate of the attitude and orbit."""
    pass


def request_attitude_star_tracker(payload):
    """Request the attitude estimate from the star tracker."""
    pass
