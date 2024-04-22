
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

def draw_landmarks_and_save(frame_obj, regions_and_landmarks, save_dir):
    """
    Draws larger centroids of landmarks on the frame, adds a larger legend for region colors, and saves the image.

    Args:
        frame_obj (Frame): The Frame object containing the image and metadata.
        regions_and_landmarks (list of tuples): Each tuple contains a region ID and a LandmarkDetectionResult.
        save_dir (str): Directory where the modified image will be saved.

    Returns:
        None
    """
    # Ensure the save directory exists
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Start with the original image from the frame object
    image = frame_obj.frame.copy()

    # Define a list of colors for different regions (in BGR format)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255)]

    # Draw each landmark with a larger circle based on its region
    region_color_map = {}
    circle_radius = 15  # Increased circle radius (3 times the original radius of 5)
    circle_thickness = -1  # Filled circle
    for idx, (region, detection_result) in enumerate(regions_and_landmarks):
        color = colors[idx % len(colors)]
        region_color_map[region] = color  # Map region ID to color for legend

        for (x, y) in detection_result.centroid_xy:
            cv2.circle(image, (int(x), int(y)), circle_radius, color, circle_thickness)

    # Add a larger legend to the image
    legend_x = 10
    legend_y = 50  # Start a bit lower to accommodate larger text
    font_scale = 1.5  # Increased font scale (3 times the original scale of 0.5)
    text_thickness = 3  # Thicker text for better visibility
    for region, color in region_color_map.items():
        cv2.putText(image, f'Region {region}', (legend_x, legend_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, text_thickness)
        legend_y += 40  # Increase spacing to prevent overlapping text entries

    # Generate a filename based on the frame ID and save the image
    filename = f"frame_{frame_obj.frame_id}.jpg"
    save_path = os.path.join(save_dir, filename)
    cv2.imwrite(save_path, image)
    print(f"Saved: {save_path}")

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
    latest_frames_w_id = cm.get_latest_frame()

    # get all available frames 
    #all_frames = cm.get_available_frames()
    # NOTE access same as prev function 

    # Prepare the frames_with_ids list for the ML pipeline
    latest_frames = []
    latest_frames_w_id = get_latest_frame(image_dir)
    for camera_id, frame_obj in latest_frames_w_id.items():
        # Ensure that the frame_obj is an instance of Frame and has the necessary attributes
        if isinstance(frame_obj, Frame) and hasattr(frame_obj, 'frame'):
            latest_frames.append(frame_obj)
    
    ml_frames = processor.process_for_ml_pipeline(latest_frames)

    for frame_obj in ml_frames:
        logger.info("reached here")
        regions_and_landmarks = pipeline.run_ml_pipeline_on_single(frame_obj)
        if regions_and_landmarks:
            # Assuming you have a Frame object and some regions and landmarks processed
            draw_landmarks_and_save(frame_obj, regions_and_landmarks, "inference_output")


if __name__ == '__main__':
    main()