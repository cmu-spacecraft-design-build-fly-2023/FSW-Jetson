"""
Payload Task List

Description: It contains the high-level tasks/activities processed by the payload.

Author: Ibrahima S. Sow
Date: [Creation or Last Update Date]
"""

import random # FOR DEBUGGING

# TODO - fill in functions
# TODO - Fill in the functions with the correct parameters and return types


# Debug
def debug_hello(payload):
    print("Hello from the payload!")
    
def debug_random_error(payload):
    if random.random() < 0.7:
        raise Exception("Random error occurred!")
    else:
        print("No error occurred.")

def debug_goodbye(payload):
    print("Goodbye from the payload!")


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
    pass

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

def request_landmarked_image(payload):
    """Request a landmarked image."""
    pass

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




