"""
Payload Tasks

Description: This file contains the high-level tasks processed by the Payload based on the requests coming from its communciation interface. 

Author: Ibrahima S. Sow
Date: [Creation or Last Update Date]
"""

from flight import message_id as msg_id
import flight.tasks as tasks

def get_task_from_id(id):
    """
    Returns the task function associated with the given task/message ID.

    Args:
        id (int): The task/message ID.

    Returns:
        function: The task function associated with the given task/message ID.
    """
    return ID_TASK_MAPPING.get(id, None)


def ID_exists(id):
    """
    Checks if the given task/message ID exists in the task/message mapping.

    Args:
        id (int): The task/message ID.

    Returns:
        bool: True if the task/message ID exists, False otherwise.
    """
    return id in ID_TASK_MAPPING


# Map task IDs to their respective functions
ID_TASK_MAPPING = {
    msg_id.SYNCHRONIZE_TIME: tasks.synchronize_time,
    msg_id.REQUEST_TIME: tasks.request_time,
    msg_id.REQUEST_PAYLOAD_STATE: tasks.request_payload_state,
    msg_id.REQUEST_PAYLOAD_MONITORING_DATA: tasks.request_payload_monitoring_data,
    msg_id.RESTART_PAYLOAD: tasks.restart_payload,
    msg_id.REQUEST_LOGS_FROM_LAST_X_SECONDS: tasks.request_logs_from_last_x_seconds,
    msg_id.DELETE_ALL_LOGS: tasks.delete_all_logs,
    msg_id.CAPTURE_AND_SEND_IMAGE: tasks.capture_and_send_image,
    msg_id.REQUEST_LAST_IMAGE: tasks.request_last_image,
    msg_id.REQUEST_IMAGE_METADATA: tasks.request_image_metadata,
    msg_id.REQUEST_IMAGE_STORAGE_INFO: tasks.request_image_storage_info,
    msg_id.CHANGE_CAMERA_RESOLUTION: tasks.change_camera_resolution,
    msg_id.DELETE_ALL_STORED_IMAGES: tasks.delete_all_stored_images,
    msg_id.REQUEST_LANDMARKED_IMAGE: tasks.request_landmarked_image,
    msg_id.REQUEST_LANDMARKED_IMAGE_METADATA: tasks.request_landmarked_image_metadata,
    msg_id.DISABLE_REGION_X: tasks.disable_region_x,
    msg_id.ENABLE_REGION_X: tasks.enable_region_x,
    msg_id.REQUEST_REGION_X_STATUS: tasks.request_region_x_status,
    msg_id.TURN_ON_CAMERAS: tasks.turn_on_cameras,
    msg_id.TURN_OFF_CAMERAS: tasks.turn_off_cameras,
    msg_id.ENABLE_CAMERA_X: tasks.enable_camera_x,
    msg_id.DISABLE_CAMERA_X: tasks.disable_camera_x,
    msg_id.REQUEST_IMAGE_STORAGE_INFO: tasks.request_image_storage_info,
    msg_id.REQUEST_CAMERA_STATUS: tasks.request_camera_status,
    # ...
    # DEBUG ONLY
    msg_id.DEBUG_HELLO: tasks.debug_hello,
    msg_id.DEBUG_RANDOM_ERROR: tasks.debug_random_error,
    msg_id.DEBUG_GOODBYE: tasks.debug_goodbye,
    msg_id.DEBUG_NUMBER: tasks.debug_number,
}
