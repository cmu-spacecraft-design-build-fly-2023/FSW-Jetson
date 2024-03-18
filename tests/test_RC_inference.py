"""
Region Classification Inference Module

This module is designed for running inference on images using the RegionClassifier class, which is assumed to be
a model capable of classifying images into predefined geographical regions. It iterates over all images in a given
directory, performs classification, and outputs the results to a CSV file. The output includes the image filename,
predicted region IDs, the actual region ID extracted from the filename, and the probabilities associated with each
prediction. Additionally, the script calculates and prints the overall accuracy of the predictions based on the
matches between predicted and actual region IDs.

Dependencies:
- PIL (Python Imaging Library): Used for opening and converting images.
- csv: Required for writing the inference results to a CSV file.
- os, sys: Needed for directory manipulation and path adjustments.

Author: Eddie
Date: [Creation or Last Update Date]
"""

import os
import sys
import csv
from PIL import Image

sys.path.append('../flight/vision')
sys.path.append('../models')

from rc import RegionClassifier

def run_rc_inference(image_dir):
    """
    Runs the region classification inference on all .jpg images within the specified directory.
    
    Args:
        image_dir (str): The directory containing the images for inference.
        
    Returns:
        list: A list of tuples, each containing the filename and the predicted regions that were correct.
    """
    output_path = 'inference_output/RC_inference_results.csv' 
    region_ids = ['53S', '32S', '52S', '54T', '33S', '10T', '11R', '17R', '12R', '16T', '33T', '32T', '10S', '18S', '54S']

    # Initialize the classifier
    classifier = RegionClassifier()

    correct_predictions = []
    total_images = 0

    with open(output_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(['Image Filename', 'Predicted Region IDs', 'Actual Region ID', 'Probabilities'])
        
        print("Region Classifier Inference Result:")
        for image_filename in os.listdir(image_dir):
            if image_filename.endswith('.jpg'):
                image_path = os.path.join(image_dir, image_filename)
                img = Image.open(image_path).convert('RGB')
                
                # Classification
                predicted_list, probabilities = classifier.classify_region(img)
                
                # Map the predicted indices to their corresponding region IDs
                predicted_region_ids = [region_ids[index] for index in predicted_list]
                predicted_region_ids_str = ', '.join(predicted_region_ids)
                
                # Extract the actual region ID from the filename
                actual_region_id = image_filename.split('_')[1]
                
                if actual_region_id in predicted_region_ids:
                    correct_predictions.append((image_filename, predicted_region_ids))
                
                total_images += 1
                
                print(f"Image: {image_filename} | Predicted: {predicted_region_ids_str} | Actual: {actual_region_id} | Probabilities: {probabilities}")

                # Write the result row to the CSV file
                writer.writerow([image_filename, predicted_region_ids_str, actual_region_id, str(probabilities)])

    accuracy = (len(correct_predictions) / total_images) * 100 if total_images > 0 else 0
    print(f"\nAccuracy: {accuracy:.2f}%")
    return correct_predictions

if __name__ == "__main__":
    image_dir = 'inference_data/RC_testdata'
    correct_predictions = run_rc_inference(image_dir)

    for filename, regions in correct_predictions:
        print(f"{filename}: {', '.join(regions)}")

    