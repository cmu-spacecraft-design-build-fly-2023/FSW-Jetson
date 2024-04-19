
from camera.camera import CameraManager
import time
import cv2
import os

def read_image_from_path(camera_id):
        images_directory = f"captured_images/camera_{camera_id}"
        image_files = os.listdir(images_directory)
        if not image_files:
            print(f"No images found for camera {camera_id}")
            return None
        latest_image_path = max(
            [os.path.join(images_directory, filename) for filename in image_files],
            key=os.path.getctime
        )
        image = cv2.imread(latest_image_path)
        window_name = "Display Image"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)  # Allows window resizing by the user
        cv2.imshow(window_name, image)  # Correct usage: Provide window name and the image
        cv2.waitKey(0)  # Wait for any key press
        cv2.destroyAllWindows() 
        return 

def main():
    # provide camera IDs connected 
    camera_ids = [0,2,4,6] 

    # create camera manager  
    cm = CameraManager(camera_ids)

    # capture frames and store images of all cameras 
    cm.capture_frames()

    # show live feed for each camera one at a time, press q to exit 
    # cm.run_live_feeds() # NOTE frames and images are being stored when this is executed

    # NOTE max of 50 images are being stored in each folder 

    # get latest frames of all cameras connected
    # return a dictionary with key as camera ID and value as latest Frame class, refer camera.py for structure of frame class 
    latest_frames = cm.get_latest_frame()
    for id in camera_ids:
        frame = latest_frames[id]
        print(frame.camera_id) # just an example on how to acess frame class

    # get all available frames 
    all_frames = cm.get_available_frames()
    # NOTE access same as prev function 

    #show the latest image of specific camera 
    read_image_from_path(0)







if __name__ == '__main__':
    main()