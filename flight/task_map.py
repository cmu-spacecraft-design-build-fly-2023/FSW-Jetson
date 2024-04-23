"""
Payload Tasks

Description: This file contains the high-level tasks processed by the Payload based on the requests coming from its communciation interface. 

Author: Ibrahima S. Sow
Date: [Creation or Last Update Date]
"""

from flight import message as msg
import flight.tasks as tasks


# Map task IDs to their respective functions
ID_TASK_MAPPING = {
    msg.SYNCHRONIZE_TIME: tasks.synchronize_time,
    msg.REQUEST_TIME: tasks.request_time,
    msg.REQUEST_PAYLOAD_STATE: tasks.request_payload_state,
    msg.REQUEST_PAYLOAD_MONITORING_DATA: tasks.request_payload_monitoring_data,
    msg.RESTART_PAYLOAD: tasks.restart_payload,
    msg.REQUEST_LOGS_FROM_LAST_X_SECONDS: tasks.request_logs_from_last_x_seconds,
    msg.DELETE_ALL_LOGS: tasks.delete_all_logs,
    msg.CAPTURE_AND_SEND_IMAGE: tasks.capture_and_send_image,
    msg.REQUEST_LAST_IMAGE: tasks.request_last_image,
    msg.REQUEST_IMAGE_METADATA: tasks.request_image_metadata,
    msg.REQUEST_IMAGE_STORAGE_INFO: tasks.request_image_storage_info,
    msg.CHANGE_CAMERA_RESOLUTION: tasks.change_camera_resolution,
    msg.DELETE_ALL_STORED_IMAGES: tasks.delete_all_stored_images,
    msg.REQUEST_LANDMARKED_IMAGE: tasks.request_landmarked_image,
    msg.REQUEST_LANDMARKED_IMAGE_METADATA: tasks.request_landmarked_image_metadata,
    msg.DISABLE_REGION_X: tasks.disable_region_x,
    msg.ENABLE_REGION_X: tasks.enable_region_x,
    msg.REQUEST_REGION_X_STATUS: tasks.request_region_x_status,
    msg.TURN_ON_CAMERAS: tasks.turn_on_cameras,
    msg.TURN_OFF_CAMERAS: tasks.turn_off_cameras,
    msg.ENABLE_CAMERA_X: tasks.enable_camera_x,
    msg.DISABLE_CAMERA_X: tasks.disable_camera_x,
    msg.REQUEST_IMAGE_STORAGE_INFO: tasks.request_image_storage_info,
    msg.REQUEST_CAMERA_STATUS: tasks.request_camera_status,
    # ...
    # DEBUG ONLY
    msg.DEBUG_HELLO: tasks.debug_hello,
    msg.DEBUG_RANDOM_ERROR: tasks.debug_random_error,
    msg.DEBUG_GOODBYE: tasks.debug_goodbye,
    msg.DEBUG_NUMBER: tasks.debug_number,
}
