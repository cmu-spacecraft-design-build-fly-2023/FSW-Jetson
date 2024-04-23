"""
Landmark Detection Inference and Evaluation Script

This script performs landmark detection inference within a specified region, evaluates the model's accuracy 
against provided image labels, and optionally visualizes the results by drawing bounding boxes around detected 
and ground truth landmarks. It calculates pixel-wise errors between detected landmarks and ground truth coordinates, 
supporting both pixel and geographical coordinates.

Usage:
    Execute the script from the command line, specifying the region ID and whether to draw bounding boxes:
    
    python <script_name>.py --region <region_id> [--draw]
    
    For example:
    python test_inference.py --region 17R --draw

What It Does:
- Performs landmark detection using a pre-trained model specified by region ID.
- Reads ground truth labels from corresponding label files and filters entries based on detected classes.
- Calculates pixel-wise errors between detected centroids and ground truth centroids for accuracy evaluation.
- Optionally draws bounding boxes around detected landmarks and ground truth landmarks for visual comparison when the --draw option is used.
- Saves the results, including detected and ground truth coordinates, class-specific errors, and mean error across all detections, to a CSV file.

Author: Eddie
"""

import cv2
import csv
import numpy as np
import argparse
import os
from os.path import isfile, join
from PIL import Image, ImageDraw
from flight.vision.ld import LandmarkDetector


def print_detected_landmarks(detection_results):
    """
    Prints a table of detected landmarks including pixel and geographical coordinates for centroids
    and bounding boxes.

    Args:
        centroid_xy (np.ndarray): Detected centroids in pixel coordinates as [x, y].
        centroid_latlons (np.ndarray): Detected centroids in geographical coordinates as [lat, lon].
    """
    # Unpack the detection results
    centroid_xy = detection_results["centroid_xy"]
    centroid_latlons = detection_results["centroid_latlons"]
    landmark_classes = detection_results["landmark_classes"]

    # Header
    print(
        f"{'Class':>10} {'Centroid X':>10} {'Centroid Y':>10} {'Centroid Lat':>15} {'Centroid Lon':>15}"
    )
    print("-" * 100)  # Adjust the number based on your column widths

    # Rows
    for landmark_cls, cent_xy, cent_latlon in zip(landmark_classes, centroid_xy, centroid_latlons):
        print(
            f"{landmark_cls:>10.2f} {cent_xy[0]:>10.2f} {cent_xy[1]:>10.2f} {cent_latlon[0]:>15.6f} {cent_latlon[1]:>15.6f}"
        )


def read_ground_truth(label_path, detected_classes, image_width, image_height):
    """
    Reads ground truth data from the label file and filters entries based on detected classes.

    Args:
        label_path (str): Path to the ground truth label file.
        detected_classes (list): List of classes detected by the model.
        image_width (int): Width of the image.
        image_height (int): Height of the image.

    Returns:
        list: Filtered ground truth boxes and centroids.
    """
    ground_truth_boxes = []
    ground_truth_centroids = []
    with open(label_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            class_id, center_x, center_y, width, height = map(float, line.split())
            if class_id not in detected_classes:
                continue
            actual_center_x = center_x * image_width
            actual_center_y = center_y * image_height
            ground_truth_centroids.append((class_id, [actual_center_x, actual_center_y]))
            left = int((center_x - width / 2) * image_width)
            top = int((center_y - height / 2) * image_height)
            right = int((center_x + width / 2) * image_width)
            bottom = int((center_y + height / 2) * image_height)
            ground_truth_boxes.append([left, top, right, bottom])
    return ground_truth_boxes, ground_truth_centroids


def calculate_errors(detected_class_centroids, ground_truth_centroids):
    """
    Calculates pixel-wise errors between detected centroids and ground truth centroids.

    Args:
        detected_class_centroids (list): Detected centroids with their classes.
        ground_truth_centroids (list): Ground truth centroids with their classes.

    Returns:
        dict, float: Class-specific errors and the mean error.
    """
    class_errors = {}
    all_errors = []
    for detected_cls, detected_centroid in detected_class_centroids:
        for gt_cls, gt_centroid in ground_truth_centroids:
            if detected_cls == gt_cls:
                error = np.linalg.norm(np.array(detected_centroid) - np.array(gt_centroid))
                class_errors[detected_cls] = error  # Store error by class
                # Add error to the list for mean calculation
                all_errors.append(error)
                break
    mean_error = np.mean(all_errors) if all_errors else float("nan")
    return class_errors, mean_error


def draw_boxes(img, ground_truth_boxes, bounding_boxes):
    """
    Draws detected and ground truth boxes on the image.

    Args:
        img (PIL.Image.Image): Image object to draw on.
        ground_truth_boxes (list): Ground truth boxes.
        bounding_boxes (list): Detected bounding boxes.

    Returns:
        PIL.Image.Image: Image object with boxes drawn.
    """
    draw = ImageDraw.Draw(img)
    for box in ground_truth_boxes:
        # Ensure box is in the format [(left, top), (right, bottom)]
        draw.rectangle([(box[0], box[1]), (box[2], box[3])], outline="green", width=5)

    for box in bounding_boxes:
        # Ensure box is in the format [(left, top), (right, bottom)]
        draw.rectangle([(box[0], box[1]), (box[2], box[3])], outline="red", width=5)
    return img


def evaluate_inference(
    image_file,
    detection_results,
    image_path,
    label_path,
    csv_writer,
    output_dir,
    draw_boxes_flag,
):
    """
    Evaluates the inference on a single image, writes the results to a CSV file, calculates pixel-wise errors,
    and optionally plots ground truth and detected bounding boxes for visual comparison based on command-line input.

    Args:
        image_file (str): Name of the image file.
        detection_results (dict): Detection results including detected centroids, classes, and bounding boxes.
        image_path (str): Path to the image file.
        label_path (str): Path to the label file.
        csv_writer (csv.writer): CSV writer object for recording results.
        output_dir (str): Directory path to save the output images.
        draw_boxes_flag (bool): Flag indicating whether to draw boxes on the image.
    """

    # Load image
    img = Image.open(image_path)
    image_width, image_height = img.size

    # Unpack detection results
    detected_centroids = detection_results["centroid_xy"]
    detected_classes = detection_results["landmark_classes"]
    bounding_boxes = detection_results["corner_xy"]
    centroid_latlons = detection_results["centroid_latlons"]

    # Read ground truth data
    ground_truth_boxes, ground_truth_centroids = read_ground_truth(
        label_path, detected_classes, image_width, image_height
    )

    # Calculate errors
    detected_class_centroids = [
        (cls, centroid) for cls, centroid in zip(detected_classes, detected_centroids)
    ]
    class_errors, mean_error = calculate_errors(detected_class_centroids, ground_truth_centroids)

    if mean_error is not None:
        print(f"Mean pixel-wise error: {mean_error}")
    else:
        print("No matching classes found for error calculation.")

    # Draw boxes if flag is set
    if draw_boxes_flag:
        img = draw_boxes(img, ground_truth_boxes, bounding_boxes)
        save_path = os.path.join(output_dir, f"{os.path.splitext(image_file)[0]}_result.jpg")
        img.save(save_path)
        print(f"Image with bounding boxes saved to {save_path}")

    # Write results to CSV
    for (detected_cls, cent_xy), cent_latlon in zip(detected_class_centroids, centroid_latlons):
        class_error = class_errors.get(
            detected_cls, float("nan")
        )  # Fetch the error for this specific class
        gt_centroid = next(
            (gt_cent for gt_cls, gt_cent in ground_truth_centroids if gt_cls == detected_cls),
            [float("nan"), float("nan")],
        )
        csv_writer.writerow(
            [
                image_file,  # Original image file name
                *gt_centroid,  # Ground Truth Centroid X, Y
                *cent_xy,  # Detected Centroid X, Y
                *cent_latlon,  # Detected Centroid Latitude, Longitude
                detected_cls,  # Class of the detected landmark
                class_error,  # Error for this specific class
                mean_error,  # Mean error across all detections
            ]
        )


def run_ld_inference_test(region_id, draw_boxes_flag=False, data_path=None):
    """
    Executes landmark detection (LD) inference on all images within a specified region.

    Args:
        region_id (str): The ID of the region for which to run landmark detection. This ID is used to
                         identify the specific directory containing the test images and labels.

    Detected landmarks and validation results are printed to the console for each image processed.
    """

    # Directory setup
    if data_path is None:
        data_path = "vision/inference_data/LD_testdata/" + region_id + "_top_salient"
    images_dir = data_path + "/img/"
    label_dir = data_path + "/label/"
    output_dir = "tests/vision/inference_output/"
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Get a list of image files in the directory
    image_files = [
        f
        for f in os.listdir(images_dir)
        if isfile(join(images_dir, f)) and f.endswith((".png", ".jpg", ".jpeg"))
    ]

    # Initialize the LandmarkDetector
    detector = LandmarkDetector(region_id=region_id)

    # CSV file setup
    csv_file_path = os.path.join(output_dir, f"{region_id}_inference_results.csv")
    with open(csv_file_path, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write the header row
        headers = [
            "Image",
            "Groundtruth X",
            "Groundtruth Y",
            "Centroid X",
            "Centroid Y",
            "Centroid Lat",
            "Centroid Lon",
            "Class Error",
            "Mean Error",
        ]
        csv_writer.writerow(headers)

        # Loop through each image file
        for image_file in image_files:
            image_path = join(images_dir, image_file)
            img = cv2.imread(image_path)

            if img is None:
                print(f"Error: Unable to load image {image_file}.")
                continue

            image_path = join(images_dir, image_file)
            label_path = join(label_dir, image_file.rsplit(".", 1)[0] + ".txt")

            # Detect landmarks
            print("----------")
            print(f"Running LD inference for {image_file}:")
            (
                centroid_xy,
                corner_xy,
                centroid_latlons,
                corner_latlons,
                landmark_classes,
            ) = detector.detect_landmarks_t(img)

            detection_results = {
                "centroid_xy": centroid_xy,
                "corner_xy": corner_xy,
                "centroid_latlons": centroid_latlons,
                "corner_latlons": corner_latlons,
                "landmark_classes": landmark_classes,
            }

            print_detected_landmarks(detection_results)
            evaluate_inference(
                image_file,
                detection_results,
                image_path,
                label_path,
                csv_writer,
                output_dir,
                draw_boxes_flag,
            )

            print(f"Inference results saved to {csv_file_path}")
            print("----------")


def run_ld_inference(
    image_path,
    region_id,
    label_path,
    draw_boxes_flag=False,
    output_dir="inference_output/",
):
    """
    Executes landmark detection (LD) inference on a single specified image.

    Args:
        image_path (str): The path to the image file for which to run landmark detection.
        region_id (str): The ID of the region for landmark detection. Used for initializing the LandmarkDetector.
        label_path (str, optional): The path to the label file for validation. Defaults to None.
        draw_boxes_flag (bool, optional): Flag to draw bounding boxes on detected landmarks. Defaults to False.
        output_dir (str, optional): The directory where inference results are saved. Defaults to 'inference_output/'.
    """

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Initialize the LandmarkDetector
    detector = LandmarkDetector(region_id=region_id)

    # CSV file setup
    csv_file_path = os.path.join(
        output_dir, f'{os.path.basename(image_path).split(".")[0]}_inference_result.csv'
    )
    with open(csv_file_path, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write the header row
        headers = [
            "Image",
            "Groundtruth X",
            "Groundtruth Y",
            "Centroid X",
            "Centroid Y",
            "Centroid Lat",
            "Centroid Lon",
            "Class Error",
            "Mean Error",
        ]
        csv_writer.writerow(headers)

        # Process the specified image
        img = cv2.imread(image_path)
        if img is None:
            print(f"Error: Unable to load image {image_path}.")
            return

        print("----------")
        print(f"Running {region_id} LD inference for {os.path.basename(image_path)}:")
        centroid_xy, corner_xy, centroid_latlons, corner_latlons, landmark_classes = (
            detector.detect_landmarks_t(img)
        )

        # Check if all results are None
        if (
            centroid_xy is None
            and corner_xy is None
            and centroid_latlons is None
            and corner_latlons is None
            and landmark_classes is None
        ):
            print("No landmarks detected. Skipping further processing.")
            return

        detection_results = {
            "centroid_xy": centroid_xy,
            "corner_xy": corner_xy,
            "centroid_latlons": centroid_latlons,
            "corner_latlons": corner_latlons,
            "landmark_classes": landmark_classes,
        }

        print_detected_landmarks(detection_results)
        evaluate_inference(
            os.path.basename(image_path),
            detection_results,
            image_path,
            label_path,
            csv_writer,
            output_dir,
            draw_boxes_flag,
        )

        print(f"Inference results saved to {csv_file_path}")
        print("----------")


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-r", "--region", required=True, help="Region ID to test specific LD inference"
    )
    parser.add_argument("--draw", action="store_true", help="Draw boxes and save result image")
    args = parser.parse_args()

    region_id = args.region
    draw_boxes_flag = args.draw

    run_ld_inference_test(region_id, draw_boxes_flag)
