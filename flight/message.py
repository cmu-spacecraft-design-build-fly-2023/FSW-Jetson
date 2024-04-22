"""
Payload Message Definition

Description: This file defines the different type of messages and their IDs. For the transmitting message, it contains the mapping to the corresponding tasks.

Author: Ibrahima S. Sow
Date: [Creation or Last Update Date]
"""


################# RX


# Time 
SYNCHRONIZE_TIME = 0x00
REQUEST_TIME = 0x01


# Payload Control
REQUEST_PAYLOAD_STATE = 0x20
REQUEST_PAYLOAD_MONITORING_DATA = 0x21
REQUEST_CAMERA_STATUS = 0x22
RESTART_PAYLOAD = 0x23
# SHUTDOWN_PAYLOAD = 0x24
REQUEST_LOGS_FROM_LAST_X_SECONDS = 0x25 # Payload sends logs from the last X seconds in payload
DELETE_ALL_LOGS = 0x26





# Camera

CAPTURE_AND_SEND_IMAGE = 0x01
REQUEST_LAST_IMAGE = 0x02
REQUEST_IMAGE = 0x03
REQUEST_IMAGE_METADATA = 0x04
REQUEST_IMAGE_STORAGE_INFO = 0x05
TURN_ON_CAMERAS = 0x06
TURN_OFF_CAMERAS = 0x07
ENABLE_CAMERA_X = 0x08
DISABLE_CAMERA_X = 0x09
REQUEST_IMAGE_STORAGE_INFO = 0x07
CHANGE_CAMERA_RESOLUTION = 0x08
DELETE_ALL_STORED_IMAGES = 0x09



# INFERENCE

REQUEST_LANDMARKED_IMAGE = 0x01
REQUEST_LANDMARKED_IMAGE_METADATA = 0x02
DISABLE_REGION_X = 0x03
ENABLE_REGION_X = 0x04
REQUEST_REGION_X_STATUS = 0x05 #  If a landmark detector is really bad
REQUEST_LAST_OBSERVATIONS_FILE = 0x06







# Attitude and Orbit Estimation


RESET_AOD_STATE = 0x00
REQUEST_AOD_LAST_ESTIMATE = 0x10
REQUEST_ATTITUDE_ESTIMATE = 0x11
REQUEST_ORBIT_ESTIMATE = 0x12
RESOLVE_STATE = 0x13 # Payload simulate forward to current time (prediction)
REQUEST_LAST_AOD_ESTIMATE_LOGS = 0x14
RUN_ATTITUDE_AND_ORBIT_ESTIMATION = 0x08





## OTA









################# TX
















