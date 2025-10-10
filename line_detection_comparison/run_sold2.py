#!/usr/bin/env python

import os
from .libs.SOLD2.run_sold2_inference import run_sold2_inference_core

# Define the project base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_sold2_inference(input_image_path, output_image_path):
    """
    Runs the SOLD2 inference.
    """
    print("--- Running SOLD2 Inference (via wrapper) ---")
    run_sold2_inference_core(input_image_path, output_image_path)
    print("--- SOLD2 Inference Complete (via wrapper) ---")

if __name__ == "__main__":
    os.makedirs(os.path.join(BASE_DIR, "output"), exist_ok=True)
    DEFAULT_INPUT_IMAGE = os.path.join(BASE_DIR, "input", "test_image.jpg")
    DEFAULT_OUTPUT_IMAGE = os.path.join(BASE_DIR, "output", "sold2_detection.png")
    run_sold2_inference(DEFAULT_INPUT_IMAGE, DEFAULT_OUTPUT_IMAGE)
    print("\nSOLD2 wrapper script finished.")
