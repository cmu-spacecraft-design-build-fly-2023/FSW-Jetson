"""
Machine Learning Pipeline for Region Classification and Landmark Detection

This script defines a machine learning pipeline that processes a series of frames from camera feeds, 
performs region classification to identify geographic regions within the frames, and subsequently 
detects landmarks within those regions. The script is designed to handle varying lighting conditions 
by discarding frames that are deemed too dark for reliable classification or detection.

Author: Eddie
Date: [Creation or Last Update Date]
"""

# import necessary modules
from PIL import Image
import cv2
from flight.vision.rc import RegionClassifier
from flight.vision.ld import LandmarkDetector
from flight import Logger
import os


class Landmark:
    """
    A class to store landmark info including centroid coordinates, geographic coordinates, and classes.

    Attributes:
        centroid_xy (list of tuples): The centroid coordinates (x, y) of detected landmarks.
        centroid_latlons (list of tuples): The geographic coordinates (latitude, longitude) of detected landmarks.
        landmark_classes (list): The classes of the detected landmarks.
    """

    def __init__(self, centroid_xy, centroid_latlons, landmark_classes):
        """
        Initializes the Landmark

        Args:
            centroid_xy (list of tuples): Centroid coordinates (x, y) of detected landmarks.
            centroid_latlons (list of tuples): Geographic coordinates (latitude, longitude) of detected landmarks.
            landmark_classes (list): Classes of detected landmarks.
        """
        self.centroid_xy = centroid_xy
        self.centroid_latlons = centroid_latlons
        self.landmark_classes = landmark_classes

    def __repr__(self):
        return f"Landmark(centroid_xy={self.centroid_xy}, centroid_latlons={self.centroid_latlons}, landmark_classes={self.landmark_classes})"


class MLPipeline:
    """
    A class representing a machine learning pipeline for processing camera feed frames for
    region classification and landmark detection.

    Attributes:
        region_classifier (RegionClassifier): An instance of RegionClassifier for classifying geographic regions in frames.
    """

    def __init__(self):
        """
        Initializes the MLPipeline class, setting up any necessary components for the machine learning tasks.
        """
        self.region_classifier = RegionClassifier()

    def classify_frame(self, frame_obj):
        """
        Classifies a frame to identify geographic regions using the region classifier.

        Args:
            frame_obj (Frame): The Frame object to classify.

        Returns:
            list: A list of predicted region IDs classified from the frame.
        """
        predicted_list = self.region_classifier.classify_region(frame_obj)
        return predicted_list

    def run_ml_pipeline_on_batch(self, frames):
        """
        Processes a series of frames, classifying each for geographic regions and detecting landmarks,
        and returns the detection results along with camera IDs.

        Args:
            frames (list of Frame): A list of Frame objects.

        Returns:
            list of tuples: Each tuple consists of the camera ID and the landmark detection results for that frame.
        """
        results = []
        for frame_obj in frames:
            pred_regions = self.classify_frame(frame_obj)
            frame_results = []
            for region in pred_regions:
                detector = LandmarkDetector(region_id=region)
                centroid_xy, centroid_latlons, landmark_classes = detector.detect_landmarks(
                    frame_obj.frame
                )
                landmark = Landmark(centroid_xy, centroid_latlons, landmark_classes)
                frame_results.append((region, landmark))
            results.append((frame_obj.camera_id, frame_results))
        return results

    def run_ml_pipeline_on_single(self, frame_obj):
        """
        Processes a single frame, classifying it for geographic regions and detecting landmarks,
        and returns the detection result along with the camera ID.

        Args:
            frame_obj (Frame): The Frame object to process.

        Returns:
            tuple: The camera ID and the landmark detection results for the frame.
        """
        Logger.log(
            "INFO",
            "------------------------------Inference---------------------------------",
        )
        pred_regions = self.classify_frame(frame_obj)
        if len(pred_regions) == 0:
            Logger.log(
                "INFO",
                f"[Camera {frame_obj.camera_id} frame {frame_obj.frame_id}] No landmarks detected. ",
            )
            return None
        frame_results = []
        for region in pred_regions:
            detector = LandmarkDetector(region_id=region)
            centroid_xy, centroid_latlons, landmark_classes = detector.detect_landmarks(frame_obj)
            if (
                centroid_xy is not None
                and centroid_latlons is not None
                and landmark_classes is not None
            ):
                landmark = Landmark(centroid_xy, centroid_latlons, landmark_classes)
                frame_results.append((region, landmark))
            else:
                continue
        return frame_results

    def visualize_landmarks(self, frame_obj, regions_and_landmarks, save_dir):
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
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (0, 255, 255),
            (255, 0, 255),
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
        font_scale = 1.5
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
        landmark_save_path = os.path.join(save_dir, "frame_w_landmarks.jpg")
        cv2.imwrite(landmark_save_path, image)

        img_save_path = os.path.join(save_dir, "frame.jpg")
        cv2.imwrite(img_save_path, frame_obj.frame)

        # Save the metadata to a text file
        metadata_path = os.path.join(save_dir, "frame_metadata.txt")
        with open(metadata_path, 'w') as f:
            f.write(f"Camera ID: {frame_obj.camera_id}\n")
            f.write(f"Timestamp: {frame_obj.timestamp}\n")
            f.write(f"Frame ID: {frame_obj.frame_id}\n")

        Logger.log(
            "INFO",
            f"[Camera {frame_obj.camera_id} frame {frame_obj.frame_id}] Landmark visualization saved to data/inference_output",
        )
