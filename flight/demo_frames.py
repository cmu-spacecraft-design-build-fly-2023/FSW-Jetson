import os
import cv2
import datetime
from itertools import cycle
from flight.vision.camera import Frame

# Global variables
image_dir = "/home/riverflame/Spacecraft/FSW-Jetson/tests/vision/data/12R"
image_files = [os.path.join(image_dir, file) for file in os.listdir(image_dir) if file.endswith(".png")]
image_files.sort()  # Sort the files if necessary
image_cycle = cycle(image_files)  # Create an endless iterator

def get_next_image_path():
    """
    This function returns the path to the next image in the cycle.
    """
    return next(image_cycle)

def get_latest_frame():
    """
    Fetches the latest frame from the specified image directory, cycling through images.
    """
    image_path = get_next_image_path()
    image = cv2.imread(image_path)
    print(f"================================================{image_path}")
    if image is not None:
        timestamp = datetime.datetime.now()
        return Frame(frame=image, camera_id=0, timestamp=timestamp)
    else:
        print(f"Failed to read image from {image_path}")
        return None