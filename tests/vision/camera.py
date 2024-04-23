from flight.vision.camera import CameraManager

from flight.logger import Logger

if __name__ == "__main__":
    # Specify the camera ID and resolution
    cam_id = [2]  # Change from set to list
    resolution = (1280, 720)

    cm = CameraManager(cam_id)
    Logger.log("INFO", f"Camera {cam_id[0]} initialized.")

    # Access functions for the specific camera ID
    if cm.get_camera(camera_id=cam_id[0]).camera_status == 1:
        cm.get_camera(camera_id=cam_id[0]).capture_frame()
        # camera.get_latest_image()
        # camera.get_live_feed()
    else:
        Logger.log("INFO", f"Camera {cam_id} is not available.")
