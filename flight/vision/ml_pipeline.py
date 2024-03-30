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
import numpy as np
from flight.vision.rc import RegionClassifier
from flight.vision.ld import LandmarkDetector

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

    def is_frame_dark(self, frame, threshold=0.5):
        """
        Determines if a given frame is too dark based on a specified threshold.
        
        Args:
            frame (np.array): The frame to analyze, as a NumPy array.
            threshold (float, optional): The threshold for deciding if a frame is considered dark. Defaults to 0.5.
        
        Returns:
            bool: True if the frame is considered too dark, False otherwise.
        """
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        dark_percentage = np.sum(gray_frame < 60) / np.prod(gray_frame.shape)
        return dark_percentage > threshold

    def classify_frame(self, frame):
        """
        Classifies a frame to identify geographic regions using the region classifier.
        
        Args:
            frame (np.array): The frame to classify, as a NumPy array.
        
        Returns:
            list: A list of predicted region IDs classified from the frame.
        """
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        predicted_list = self.region_classifier.classify_region_ids(frame_pil)
        return predicted_list

    def run_ml_pipeline(self, frames_with_ids):
        """
        Processes a series of frames, classifying each for geographic regions and detecting landmarks
        within those regions if the frame is not too dark.
        
        Args:
            frames_with_ids (list of tuples): A list where each element is a tuple consisting of
                                              a frame (as a NumPy array) and its associated camera ID.
        """
        for frame, camera_id in frames_with_ids:
            if not self.is_frame_dark(frame):
                pred_regions = self.classify_frame(frame)
                print(f"Camera ID {camera_id} detected regions:", pred_regions)
                for region in pred_regions:
                    detector = LandmarkDetector(region_id=region)
                    centroid_xy, centroid_latlons, landmark_classes = detector.detect_landmarks(frame)
                    print(f"    Region {region} Landmarks: {centroid_xy}, {centroid_latlons}, {landmark_classes}")
            else:
                print(f"Camera ID {camera_id}: Frame is too dark and was skipped.")