"""
Full Inference Pipeline Runner

This script is designed to orchestrate the process of landmark detection in images using a combination of region classification
and landmark detection algorithms. Initially, it identifies regions of interest within images through a region classification 
inference step. Subsequently, it applies a landmark detection algorithm to these identified regions to detect landmarks. 
The script is structured to first segregate images based on predicted regions and then perform detailed landmark detection 
within these regions.

Usage:
The script is intended to be used as a module in a larger system for image processing or as a standalone script for batch 
processing of images for landmark detection tasks.

Author: Eddie
Date: [Creation or Last Update Date]
"""

import os
from test_RC_inference import run_rc_inference
from test_LD_inference import run_ld_inference

class InferenceRunner:
    """
    A class to perform landmark detection using a pretrained YOLO model.

    Attributes:
        image_dir (str): Directory containing images for inference.
        label_dir (str): Directory containing labels for images.
    """

    def __init__(self, image_dir, label_dir):
        """
        Initializes the LandmarkDetector with image and label directories.

        Parameters:
            image_dir (str): Directory containing images for inference.
            label_dir (str): Directory containing labels for images.
        """
        self.image_dir = image_dir
        self.label_dir = label_dir

    def run_region_classification(self):
        """
        Runs the region classification inference to identify correct predictions.

        Returns:
            list: A list of tuples, each containing a filename and a list of regions.
        """
        return run_rc_inference(self.image_dir)

    def run_landmark_detection(self, correct_predictions):
        """
        Processes images based on region classification results to detect landmarks.

        Parameters:
            correct_predictions (list): A list of tuples from region classification containing filenames and regions.
        """
        for filename, regions in correct_predictions:
            for region in regions:
                image_path = os.path.join(self.image_dir, filename)
                label_path = os.path.join(self.label_dir, filename.replace('.jpg', '.txt'))  # Adjust if label files have a different extension
                run_ld_inference(image_path, region, label_path, draw_boxes_flag=False)

    def display_correct_predictions(self, correct_predictions):
        """
        Displays filenames and their correctly predicted regions.

        Parameters:
            correct_predictions (list): A list of tuples containing filenames and regions.
        """
        for filename, regions in correct_predictions:
            print(f"{filename}: {', '.join(regions)}")

if __name__ == "__main__":
    # Specify directories for images and labels
    image_dir = 'data/full_inference/img'
    label_dir = 'data/full_inference/label'

    # Initialize the InferenceRunner
    detector = InferenceRunner(image_dir, label_dir)

    # Run region classification and store correct predictions
    correct_predictions = detector.run_region_classification()

    # Display correct predictions
    detector.display_correct_predictions(correct_predictions)

    # Run landmark detection based on correct region predictions
    detector.run_landmark_detection(correct_predictions)