"""
Fake Camera Feed Generator

This module defines the FakeCameraFeed class for simulating camera feeds in machine learning and computer vision testing environments. It allows for the generation of virtual frames with specified dimensions and colors, facilitating the testing of image processing pipelines without the need for real camera hardware. Frames can be individually customized or produced in a sequence with controlled variations.

Author: Eddie
Date: [Creation or Last Update Date]
"""

import numpy as np


class FakeCameraFeed:
    def __init__(self, frame_width=640, frame_height=480):
        """
        Initializes the fake camera feed with default frame dimensions.

        Args:
            frame_width (int): The width of the frames.
            frame_height (int): The height of the frames.
        """
        self.frame_width = frame_width
        self.frame_height = frame_height

    def generate_frame(self, frame_id, frame_color=(0, 255, 0)):
        """
        Generates a single virtual frame with a specified color.

        Args:
            frame_id (int): ID number for the frame, used to vary the frame in some way if desired.
            frame_color (tuple): BGR color of the frame.

        Returns:
            numpy.ndarray: The generated frame.
        """
        frame = np.zeros((self.frame_height, self.frame_width, 3), np.uint8)
        frame[:] = frame_color
        return frame

    def get_frames(self, num_frames=6):
        """
        Generates a specified number of frames.

        Args:
            num_frames (int): The number of frames to generate.

        Returns:
            generator of numpy.ndarray: A generator that yields frames.
        """
        for camera_id in range(1, num_frames + 1):
            # Example variation in color for demonstration
            yield self.generate_frame(camera_id, frame_color=(0, 255, camera_id * 40)), camera_id
