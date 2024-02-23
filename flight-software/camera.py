from cam_interface import Camera

if __name__ == "__main__":
    # Specify the camera ID and resolution
    camera_id = 2
    resolution = (1280, 720)  
    
    camera = Camera(camera_id, resolution)
    
    # Access functions for the specific camera ID
    if camera.camera_status == 1:
        camera.capture_image()  
        # camera.get_latest_image()  
        # camera.get_live_feed()  
    else:
        print(f"Camera {camera_id} is not available.")
