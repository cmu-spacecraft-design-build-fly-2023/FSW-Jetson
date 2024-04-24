"""
Main Execution Script for ML Pipeline with Fake Camera Feed

- Retrieves frames with IDs from a simulated camera feed
- Uses FrameProcessor to filter frames suitable for ML inference
- Applies ML pipeline on the filtered batch of frames for region classification and landmark detection
- Prints detected landmarks for each frame and corresponding camera ID

Requirement:
    Set the PYTHONPATH environment variable to include the root of project to make the package flight discoverable.
    export PYTHONPATH="/path/to/project_root:$PYTHONPATH"

Author: Eddie
Date: [Creation or Last Update Date]
"""

from collections import Counter
from flight.vision.camera import Frame
from flight.vision import MLPipeline, FrameProcessor
from flight import Logger
import os
import cv2
import sys
import datetime
import logging

# Configure and initialize logger for demo
"""Logger.configure(log_level=logging.DEBUG, log_file="log/payload.log")
Logger.initialize_log(
    module_name=sys.modules[__name__],
    init_msg="Logger purpose: To capture all operational logs for debugging and monitoring system performance.",
)"""



def get_latest_frame(image_dir):
    frame_objects = {}
    # List all files in the directory and filter out non-jpg files
    all_files = [f for f in os.listdir(image_dir) if f.endswith(".png")]
    # Optionally sort files if they are not in the desired order
    all_files.sort()
    # Process only the top five images
    top_files = all_files[:20]

    for i, filename in enumerate(top_files):
        image_path = os.path.join(image_dir, filename)
        image = cv2.imread(image_path)
        if image is not None:
            timestamp = datetime.datetime.now()
            frame_obj = Frame(frame=image, camera_id=i, timestamp=timestamp)
            frame_objects[i] = frame_obj
        else:
            print(f"Failed to read image from {image_path}")
    return frame_objects


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
    colors = [
        (0, 0, 255),      # Red
        (180, 105, 255),  # Pink
        (0, 165, 255),    # Orange
        (255, 0, 0),      # Blue
        (0, 255, 0),      # Green
    ]

    # Draw each landmark with a larger circle based on its region
    region_color_map = {}
    # Increased circle radius (3 times the original radius of 5)
    circle_radius = 10
    circle_thickness = -1  # Filled circle
    for idx, (region, detection_result) in enumerate(regions_and_landmarks):
        color = colors[idx % len(colors)]
        region_color_map[region] = color  # Map region ID to color for legend

        for x, y in detection_result.centroid_xy:
            cv2.circle(image, (int(x), int(y)), circle_radius, color, circle_thickness)

    # Add a larger legend to the image
    legend_x = 10
    legend_y = 50  # Start a bit lower to accommodate larger text
    # Increased font scale (3 times the original scale of 0.5)
    font_scale = 2
    text_thickness = 3  # Thicker text for better visibility
    for region, color in region_color_map.items():
        cv2.putText(
            image,
            f"Region {region}",
            (legend_x, legend_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            text_thickness,
        )
        legend_y += 40  # Increase spacing to prevent overlapping text entries

    # Generate a filename based on the frame ID and save the image
    filename = f"frame_{frame_obj.frame_id}.jpg"
    save_path = os.path.join(save_dir, filename)
    cv2.imwrite(save_path, image)
    print(f"Saved: {save_path}")


if __name__ == "__main__":
    relative_path = "data/inference_input"
    image_dir = os.path.join(os.getcwd(), relative_path.strip("/"))
    processor = FrameProcessor()
    pipeline = MLPipeline()

    latest_frames = []
    latest_frames_w_id = get_latest_frame(image_dir)
    for camera_id, frame_obj in latest_frames_w_id.items():
        # Ensure that the frame_obj is an instance of Frame and has the necessary attributes
        if isinstance(frame_obj, Frame) and hasattr(frame_obj, "frame"):
            latest_frames.append(frame_obj)

    ml_frames = processor.process_for_ml_pipeline(latest_frames)

    for frame_obj in ml_frames:
        regions_and_landmarks = pipeline.run_ml_pipeline_on_single(frame_obj)
        if regions_and_landmarks:
            # Assuming you have a Frame object and some regions and landmarks processed
            draw_landmarks_and_save(frame_obj, regions_and_landmarks, "inference_output")
