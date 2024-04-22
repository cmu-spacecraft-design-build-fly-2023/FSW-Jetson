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
logger = Logger.get_logger()

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
                centroid_xy, centroid_latlons, landmark_classes = (
                    detector.detect_landmarks(frame_obj.frame)
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
        logger.info("------------------------------Inference---------------------------------")
        pred_regions = self.classify_frame(frame_obj)
        frame_results = []
        for region in pred_regions:
            detector = LandmarkDetector(region_id=region)
            centroid_xy, centroid_latlons, landmark_classes = detector.detect_landmarks(
                frame_obj
            )
            if centroid_xy is not None and centroid_latlons is not None and landmark_classes is not None:
                landmark = Landmark(centroid_xy, centroid_latlons, landmark_classes)
                frame_results.append((region, landmark))
            else:
                continue
        return frame_results