"""
Messgae Encoding

Description: This file contains a set of functions to encode and decode messages for UART communication.

Author(s): Ibrahima S. Sow
Date: [Creation or Last Update Date]
"""

from struct import pack, unpack
from flight.communication.message import Message
from flight.message_id import *
from flight.vision.camera import Frame





def encode_image_transmission_message(img):
    """
    Encodes an image transmission message.

    Args:
        img (numpy.ndarray): The image data to be sent.

    Returns:
        bytes: The encoded message.
    """

    img_bytes = img.tobytes()
    return Message(TRANSMIT_IMAGE, img_bytes)


if __name__ == "__main__":

    import cv2
    img = cv2.imread('tests/vision/data/12R/l9_12R_00000.png')
    img = cv2.resize(img, (640, 480))

    encoded_msg = encode_image_transmission_message(img)
    print(encoded_msg)