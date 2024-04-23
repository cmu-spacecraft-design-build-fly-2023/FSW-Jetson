"""
Payload Task List

Description: It contains the high-level tasks/activities processed by the payload.

Author: Ibrahima S. Sow
Date: [Creation or Last Update Date]
"""

from flight.logger import Logger
from flight.demo_frames import get_latest_frame # Function to provide frames insequence
from flight.vision import MLPipeline

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

# =====unitility=====
def parse_metadata(metadata_path):
    """ Parse metadata file to extract camera ID, timestamp and frame ID """
    with open(metadata_path, 'r') as file:
        metadata = file.read()
    lines = metadata.split('\n')
    camera_id = int(lines[0].split(': ')[1])
    timestamp = datetime.datetime.strptime(lines[1].split(': ')[1], '%Y-%m-%d %H:%M:%S.%f')
    frame_id = lines[2].split(': ')[1]
    return camera_id, timestamp, frame_id
# =====unitility=====

def run_ml_pipeline(payload):
    """
    Function to run ML pipeline on the latest frame retrieved from a cycling list of images.
    """
    pipeline = MLPipeline()
    latest_frame = get_latest_frame()
    if latest_frame is not None:
        regions_and_landmarks = pipeline.run_ml_pipeline_on_single(latest_frame)
        if regions_and_landmarks is not None:
            pipeline.visualize_landmarks(latest_frame, regions_and_landmarks, "data/inference_output")
    #else:
    #    print("No frame available to process.")

def request_landmarked_image(payload):
    """Request the latest landmarked image based on timestamp."""
    image_dir = "data/inference_output"
    metadata_dir = Path(image_dir)
    latest_timestamp = None
    latest_metadata_file = None

    # Scan all metadata files to find the latest one
    for metadata_file in metadata_dir.glob('frame_*.txt'):
        camera_id, timestamp, frame_id = parse_metadata(metadata_file)
        if latest_timestamp is None or timestamp > latest_timestamp:
            latest_timestamp = timestamp
            latest_metadata_file = metadata_file

    if not latest_metadata_file:
        return None

    # Extract the frame ID from the file name
    frame_id = latest_metadata_file.stem.split('_')[1]

    # Load the corresponding image
    image_path = metadata_dir / f'frame_{frame_id}.jpg'
    image = cv2.imread(str(image_path))

    if image is not None:
        # Create and return the Frame object
        camera_id, timestamp, frame_id = parse_metadata(latest_metadata_file)
        return Frame(frame=image, camera_id=camera_id, timestamp=timestamp)
    else:
        print(f"Failed to load image from {image_path}")
        return None


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
