"""
Region Classification Module

This module defines the RegionClassifier class, which leverages a pretrained EfficientNet model to classify 
images based on geographic regions. The classifier is tailored to recognize specific regions by adjusting the 
final layer to match the number of target classes and loading custom model weights. Main functionalities 
include image preprocessing and the execution of classification, providing class probabilities for each 
recognized region.


Author: Eddie
Date: [Creation or Last Update Date]
"""

import os
import yaml
import cv2
from PIL import Image
import torch
import torch.nn.functional as F
from torchvision import transforms
from efficientnet_pytorch import EfficientNet

LD_MODEL_SUF = ".pth"
NUM_CLASS = 16

from flight import Logger
logger = Logger.get_logger()

# Define error and info messages
error_messages = {
    'CONFIGURATION_ERROR': "Configuration error.",
    'MODEL_LOADING_FAILED': "Failed to load model.",
    'CLASSIFICATION_FAILED': "Classification process failed."
}

info_messages = {
    'INITIALIZATION_START': "Initializing RegionClassifier.",
    'MODEL_LOADED': "Model loaded successfully.",
    'CLASSIFICATION_START': "Starting the classification process."
}

class RegionClassifier:
    def __init__(self, model_name="efficientnet-b0"):
        """
        Initializes the RegionClassifier with a specified EfficientNet model and custom weights.

        Parameters:
            model_path (str): Path to the directory containing the model weights.
            model_name (str): Name of the EfficientNet model variant to use.
        """

        logger.info(info_messages['INITIALIZATION_START'])

        model_path, config_path = self.construct_paths()

        try:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            # Initialize the model for the specified number of classes
            self.model = EfficientNet.from_pretrained(model_name, num_classes=NUM_CLASS)

            # Adjust final layer to match number of classes
            in_features = (
                self.model._fc.in_features
            )  # Get the number of input features for the final layer
            self.model._fc = torch.nn.Linear(
                in_features, NUM_CLASS
            )  # Adjust the final layer

            # Load Custom model weights
            self.model.load_state_dict( 
                torch.load(
                    os.path.join(model_path, "model_effnet_0.997_acc" + LD_MODEL_SUF),
                    map_location=self.device,
                )
            )
            self.model = self.model.to(self.device)
            self.model.eval()
            logger.info(info_messages['MODEL_LOADED'])

        except Exception as e:
            logger.error(f"{error_messages['MODEL_LOADING_FAILED']}: {e}")
            raise

        # Define the preprocessing
        self.transforms = transforms.Compose(
            [
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
                ),
            ]
        )

        self.region_ids = self.load_region_ids(config_path)

    def construct_paths(self):
        model_path = os.path.join("models/rc")
        config_path = os.path.join("configuration/inference_config.yml")
        return model_path, config_path

    def load_region_ids(self, config_path):
        region_ids = []
        try:
            # Load the configuration file
            with open(config_path, "r") as file:
                config = yaml.safe_load(file)

            # Extract region_ids from the configuration file
            region_ids = config.get("region_ids", [])

        except Exception as e:
            logger.error(f"{error_messages['CONFIGURATION_ERROR']}: {e}")
            raise

        return region_ids

    def classify_region_ids(self, img):
        """
        Classifies a single image into one of the predefined regions.

        Parameters:
            img (PIL.Image): The input image to classify.

        Returns:
            tuple: A tuple containing two lists; the first list contains the class IDs with probabilities
            above a threshold, and the second list contains the corresponding probabilities.
        """
        logger.info(info_messages['CLASSIFICATION_START'])
        predicted_region_ids = []
        try:
            img = self.transforms(img).unsqueeze(0)  # Add batch dimension
            img = img.to(self.device)

            with torch.no_grad():
                outputs = self.model(img)
                probabilities = F.softmax(
                    outputs, dim=1
                )  # Apply softmax to convert to probabilities
                # _, predicted = torch.max(probabilities, 1)  # Get the class with the highest probability

                # Filter classes with probabilities greater than a threshold (close to zero)
                threshold = 1e-6  # Small threshold to account for floating-point precision
                probs_mask = probabilities > threshold
                probs = probabilities[probs_mask]
                classes = torch.arange(probabilities.size(1))[probs_mask.squeeze()]

                # Convert to lists for easier handling outside PyTorch
                probs.squeeze().tolist()
                classes_list = classes.tolist()

                predicted_region_ids = [self.region_ids[index] for index in classes_list]
                
        except Exception as e:
            logger.error(f"{error_messages['CLASSIFICATION_FAILED']}: {e}")
            raise

        return predicted_region_ids

    def classify_region(self, frame_obj):
        """
        Classifies a single image into one of the predefined regions.

        Parameters:
            img (PIL.Image): The input image to classify.

        Returns:
            tuple: A tuple containing two lists; the first list contains the class IDs with probabilities
            above a threshold, and the second list contains the corresponding probabilities.
        """
        # Logging the classification start with timestamp information
        logger.info(f"[Camera {frame_obj.camera_id} frame {frame_obj.frame_id}] {info_messages['CLASSIFICATION_START']}")
        predicted_region_ids = []
        
        try:
            img = Image.fromarray(cv2.cvtColor(frame_obj.frame, cv2.COLOR_BGR2RGB))
            img = self.transforms(img).unsqueeze(0)  # Add batch dimension
            img = img.to(self.device)

            with torch.no_grad():
                outputs = self.model(img)
                probabilities = F.softmax(
                    outputs, dim=1
                )  # Apply softmax to convert to probabilities
                # _, predicted = torch.max(probabilities, 1)  # Get the class with the highest probability

                # Filter classes with probabilities greater than a threshold (close to zero)
                threshold = 1e-6  # Small threshold to account for floating-point precision
                probs_mask = probabilities > threshold
                probs = probabilities[probs_mask]
                classes = torch.arange(probabilities.size(1))[probs_mask.squeeze()]

                # Convert to lists for easier handling outside PyTorch
                probs.squeeze().tolist()
                classes_list = classes.tolist()

                predicted_region_ids = [self.region_ids[index] for index in classes_list]
                
        except Exception as e:
            logger.error(f"{error_messages['CLASSIFICATION_FAILED']}: {e}")
            raise

        logger.info(f"[Camera {frame_obj.camera_id} frame {frame_obj.frame_id}] {predicted_region_ids} region(s) identified.")
        return predicted_region_ids
