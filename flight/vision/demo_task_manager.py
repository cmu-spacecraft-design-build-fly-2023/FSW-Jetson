
from camera.camera import CameraManager, Frame
from flight.vision import MLPipeline, FrameProcessor
import time
import cv2
import os
from flight.logger import logger_instance as logger

logger.clear_log()

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

def print_ml_frames(ml_frames):
    # Counting using Counter from the collections module
    camera_ids = [camera_id for _, camera_id in ml_frames]
    camera_counts = Counter(camera_ids)

    for camera_id, count in camera_counts.items():
        print(f"Camera ID {camera_id} has {count} images processed for ML pipeline.")


def print_pipeline_results(results):
    """
    Prints the results from the ML pipeline batch processing.

    Args:
        results (list of tuples): Each tuple contains a camera ID and a list of tuples,
                                  each of which contains a region ID and a LandmarkDetectionResult object.
    """
    for camera_id, regions_and_landmarks in results:
        for region, detection_result in regions_and_landmarks:
            centroid_xy = detection_result.centroid_xy
            centroid_latlons = detection_result.centroid_latlons
            landmark_classes = detection_result.landmark_classes
            print(
                f"Camera {camera_id}: Region {region} Landmarks: {centroid_xy}, {centroid_latlons}, {landmark_classes}"
            )

def main():
    # provide camera IDs connected 
    camera_ids = [0] 

    # create camera manager  
    cm = CameraManager(camera_ids, "/home/riverflame/Spacecraft/FSW-Jetson/configuration/camera_configuration.yml")
    processor = FrameProcessor()
    pipeline = MLPipeline()

    # capture frames and store images of all cameras 
    cm.capture_frames()

    # show live feed for each camera one at a time, press q to exit 
    # cm.run_live_feeds() # NOTE frames and images are being stored when this is executed

    # NOTE max of 50 images are being stored in each folder 

    # get latest frames of all cameras connected
    # return a dictionary with key as camera ID and value as latest Frame class, refer camera.py for structure of frame class 
    latest_frames = cm.get_latest_frame()

    # get all available frames 
    #all_frames = cm.get_available_frames()
    # NOTE access same as prev function 

    # Prepare the frames_with_ids list for the ML pipeline
    frames_with_ids = []
    for camera_id, frame_obj in latest_frames.items():
        # Ensure that the frame_obj is an instance of Frame and has the necessary attributes
        if isinstance(frame_obj, Frame) and hasattr(frame_obj, 'frame'):
            frames_with_ids.append((frame_obj.frame, camera_id))
    
    ml_frames = processor.process_for_ml_pipeline(frames_with_ids)
    result = pipeline.run_ml_pipeline_on_batch(ml_frames)

    print_ml_frames(ml_frames)
    print_pipeline_results(result)


if __name__ == '__main__':
    main()