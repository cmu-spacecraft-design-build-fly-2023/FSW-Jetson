"""
Frame Processing Module for Vision-Based Systems

This module defines a FrameProcessor class that preprocesses video frames for different analytical tasks in vision-based systems. 
The primary focus of this class is to filter and prepare frames based on specific criteria such as brightness levels, which can 
significantly impact the performance and accuracy of downstream processing tasks, such as ml pipelines and star tracking algorithms.
Frames are processed in batches, with each frame being associated with a camera ID. 

Author: Eddie
Date: [Creation or Last Update Date]
"""

import cv2
import numpy as np


class FrameProcessor:
    """
    A class for preprocessing frames along with their IDs based on specific requirements for further analysis.

    This class includes methods to prepare frames and their IDs for different downstream tasks such as machine learning pipelines or star tracking, based on characteristics like darkness level.
    """

    def __init__(self):
        """
        Initializes the FrameProcessor class.
        """
        pass

    def process_for_ml_pipeline(
        self, frames_with_ids, dark_threshold=0.5, brightness_threshold=60
    ):
        """
        Processes frames to select those suitable for machine learning pipeline processing, based on darkness level and potentially other criteria. Each frame is associated with an ID.

        Args:
            frames_with_ids (list of tuples): The frames and their IDs to process, as a list of tuples, each containing a frame (np.array) and its associated ID.
            dark_threshold (float, optional): The threshold for deciding if a frame is too dark for ML processing. Defaults to 0.5.
            brightness_threshold (int, optional): The pixel intensity threshold below which pixels are considered dark. Defaults to 60.

        Returns:
            list of tuples: Each tuple consists of a frame suitable for ML pipeline processing and its associated ID.
        """
        suitable_frames_with_ids = []
        for frame, camera_id in frames_with_ids:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            dark_percentage = np.sum(gray_frame < brightness_threshold) / np.prod(
                gray_frame.shape
            )
            if dark_percentage <= dark_threshold:
                suitable_frames_with_ids.append((frame, camera_id))
        return suitable_frames_with_ids

    def process_for_star_tracker(
        self, frames_with_ids, dark_threshold=0.5, brightness_threshold=60
    ):
        """
        Processes frames to select those potentially suitable for star tracker processing or other uses where high darkness levels are acceptable or required. Each frame is associated with an ID.

        Args:
            frames_with_ids (list of tuples): The frames and their IDs to process, as a list of tuples, each containing a frame (np.array) and its associated ID.
            dark_threshold (float, optional): The threshold for selecting darker frames suitable for tasks like star tracking. Defaults to 0.5.
            brightness_threshold (int, optional): The pixel intensity threshold below which pixels are considered dark. Defaults to 60.

        Returns:
            list of tuples: Each tuple consists of a frame suitable for star tracker processing or similar tasks and its associated ID.
        """
        suitable_frames_with_ids = []
        for frame, camera_id in frames_with_ids:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            dark_percentage = np.sum(gray_frame < brightness_threshold) / np.prod(
                gray_frame.shape
            )
            if dark_percentage > dark_threshold:
                suitable_frames_with_ids.append((frame, camera_id))
        return suitable_frames_with_ids
