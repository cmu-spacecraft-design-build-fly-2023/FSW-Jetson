"""
Landmark Detection Module

This module defines the LandmarkDetector class, which utilizes a pretrained YOLO (You Only Look Once) model
to detect and process landmarks within images. The detector extracts landmarks as bounding boxes along with
their associated class IDs and confidence scores. The main functionality revolves around the detection of
landmarks in given images and the extraction of useful information such as centroids and class/confidence data.

Dependencies:
- numpy: Used for array manipulations and handling numerical operations.
- cv2 (OpenCV): Required for image processing tasks.
- ultralytics YOLO: The YOLO model implementation from Ultralytics, used for object detection tasks. (Large package warning)

Author: Eddie, Haochen
Date: [Creation or Last Update Date]
"""

import numpy as np
import cv2
from ultralytics import YOLO
import os
import sys
import csv


LD_MODEL_SUF = '_nadir.pt'

class LandmarkDetector:

    def __init__(self, region_id, model_path='models/ld'):
        """
        Initialize the LandmarkDetector with a specific region ID and model path
        The YOLO object is created with the path to a specific pretrained model
        """
        self.region_id = region_id
        self.model = YOLO(os.path.join(model_path, region_id, region_id + LD_MODEL_SUF))
        self.ground_truth = self.load_ground_truth(os.path.join(model_path, region_id, f'{region_id}_top_salient.csv'))

    def load_ground_truth(self, ground_truth_path):
        """
        Loads ground truth bounding box coordinates from a CSV file.
        
        Args:
            ground_truth_path (str): Path to the ground truth CSV file.

        Returns:
            list of tuples: Each tuple contains (top_left_lon, top_left_lat, bottom_right_lon, bottom_right_lat)
        """
        ground_truth = []
        with open(ground_truth_path, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)  # Skip the header row
            for row in csvreader:
                ground_truth.append((float(row[0]), float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5])))
        return ground_truth

    def calculate_bounding_boxes(self, centroid_xy, landmark_wh):
        """
        Calculate the top-left and bottom-right coordinates of bounding boxes from centroids and dimensions.

        Args:
            centroid_xy (np.ndarray): Centroid coordinates of the landmarks as [x, y].
            landmark_wh (np.ndarray): Dimensions of the landmarks as [width, height].

        Returns:
            np.ndarray: An array of shape (n, 4), with each row containing the top-left and bottom-right coordinates of the bounding boxes.
        """
        # Calculate the top-left and bottom-right coordinates of the bounding boxes
        top_left = centroid_xy - landmark_wh / 2
        bottom_right = centroid_xy + landmark_wh / 2

        # Combine top-left and bottom-right into a single numpy array of shape (n, 4)
        bounding_boxes = np.hstack((top_left, bottom_right))

        return bounding_boxes

    def get_latlons(self, bbox_indexes):
        """
        Get the latitude and longitude for each detected bounding box based on class index.

        Args:
            bbox_indexes (list of int): Indexes of bounding boxes in the ground truth data.

        Returns:
            np.ndarray: Array of bounding box latitudes and longitudes.
        """
        centroids = []
        corners = []
        for index in bbox_indexes:
            centroid_lon, centroid_lat, top_left_lon, top_left_lat, bottom_right_lon, bottom_right_lat = self.ground_truth[index]
            corners.append([top_left_lon, top_left_lat, bottom_right_lon, bottom_right_lat])
            centroids.append([centroid_lon, centroid_lat])
        return np.array(centroids), np.array(corners)

    def detect_landmarks_t(self, img):
        """
        Detects landmarks in an input image using a pretrained YOLO model and extracts relevant information.

        Args:
            img (np.ndarray): The input image array on which to perform landmark detection.

        Returns:
            tuple: A tuple containing several numpy arrays:
                - centroid_xy (np.ndarray): Array of [x, y] coordinates for the centroids of detected landmarks.
                - corner_xy (np.ndarray): Array of bounding box corner coordinates in the format [top-left-x, top-left-y, bottom-right-x, bottom-right-y].
                - centroid_latlons (np.ndarray): Array of geographical coordinates [latitude, longitude] for each detected landmark's centroid, based on class ID.
                - corner_latlons (np.ndarray): Array of geographical coordinates for the corners of bounding boxes, similar to centroid_latlons but for box corners.
                - landmark_class (np.ndarray): Array of class IDs for each detected landmark.
        
        The detection process filters out landmarks with low confidence scores (below 0.5) and invalid bounding box dimensions. It aims to provide a comprehensive set of data for each detected landmark, facilitating further analysis or processing.
        """
        # Detect landmarks using the YOLO model
        results = self.model(img)
        landmark_list = []
        
        # Process each detection result from the model
        for result in results:
            landmarks = result.boxes

            if landmarks:# Sanity Check
                # Iterate over each detected bounding box (landmark)
                for landmark in landmarks:
                    x, y, w, h = landmark.xywh[0]
                    cls = landmark.cls[0].item()
                    conf = landmark.conf[0].item()

                    # Validate bounding box dimensions (e.g., non-negative)
                    if w < 0 or h < 0:
                        print("Invalid bounding box dimensions detected.")
                        continue

                    # Validate confidence level (e.g., consider only high confidence detections)
                    if conf < 0.5:  # Assuming 0.5 as a threshold for confidence
                        print("Skipping low confidence landmark.")
                        continue

                    landmark_list.append([int(x.item()), int(y.item()), cls, int(w.item()), int(h.item())])
            else:
                return None, None, None, None, None

        landmark_arr = np.array(landmark_list)

        # Extract centroid coordinates, class IDs, and dimensions (width and height)
        centroid_xy = landmark_arr[:, :2]  # Centroid coordinates [x, y]
        landmark_class = landmark_arr[:, 2].astype(int)  # Class IDs as integers
        landmark_wh = landmark_arr[:, 3:5]  # Width and height [w, h]

        # Calculate the top-left and bottom-right coordinates of the bounding boxes
        corner_xy = self.calculate_bounding_boxes(centroid_xy, landmark_wh)

        # Get bounding box lat/lon based on ground truth 
        centroid_latlons, corner_latlons = self.get_latlons(landmark_class)

        return centroid_xy, corner_xy, centroid_latlons, corner_latlons, landmark_class


    def detect_landmarks(self, img):
        """
        Detects landmarks in an input image using a pretrained YOLO model and extracts relevant information.

        Args:
            img (np.ndarray): The input image array on which to perform landmark detection.

        Returns:
            tuple: A tuple containing several numpy arrays:
                - centroid_xy (np.ndarray): Array of [x, y] coordinates for the centroids of detected landmarks.
                - corner_xy (np.ndarray): Array of bounding box corner coordinates in the format [top-left-x, top-left-y, bottom-right-x, bottom-right-y].
                - centroid_latlons (np.ndarray): Array of geographical coordinates [latitude, longitude] for each detected landmark's centroid, based on class ID.
                - corner_latlons (np.ndarray): Array of geographical coordinates for the corners of bounding boxes, similar to centroid_latlons but for box corners.
                - landmark_class (np.ndarray): Array of class IDs for each detected landmark.
        
        The detection process filters out landmarks with low confidence scores (below 0.5) and invalid bounding box dimensions. It aims to provide a comprehensive set of data for each detected landmark, facilitating further analysis or processing.
        """
        # Detect landmarks using the YOLO model
        results = self.model(img)
        landmark_list = []
        
        # Process each detection result from the model
        for result in results:
            landmarks = result.boxes

            if landmarks:# Sanity Check
                # Iterate over each detected bounding box (landmark)
                for landmark in landmarks:
                    x, y, w, h = landmark.xywh[0]
                    cls = landmark.cls[0].item()
                    conf = landmark.conf[0].item()

                    # Validate bounding box dimensions (e.g., non-negative)
                    if w < 0 or h < 0:
                        print("Invalid bounding box dimensions detected.")
                        continue

                    # Validate confidence level (e.g., consider only high confidence detections)
                    if conf < 0.5:  # Assuming 0.5 as a threshold for confidence
                        print("Skipping low confidence landmark.")
                        continue

                    landmark_list.append([int(x.item()), int(y.item()), cls, int(w.item()), int(h.item())])
            else:
                return None, None, None

        landmark_arr = np.array(landmark_list)

        # Extract centroid coordinates, class IDs, and dimensions (width and height)
        centroid_xy = landmark_arr[:, :2]  # Centroid coordinates [x, y]
        landmark_class = landmark_arr[:, 2].astype(int)  # Class IDs as integers
        landmark_wh = landmark_arr[:, 3:5]  # Width and height [w, h]

        # Calculate the top-left and bottom-right coordinates of the bounding boxes
        corner_xy = self.calculate_bounding_boxes(centroid_xy, landmark_wh)

        # Get bounding box lat/lon based on ground truth 
        centroid_latlons, corner_latlons = self.get_latlons(landmark_class)

        return centroid_xy, centroid_latlons, landmark_class