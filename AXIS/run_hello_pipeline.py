# AXIS/run_hello_pipeline.py

import cv2
import os
import sys

# Add src to python path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from pipeline import Pipeline, FrameContextBuilder
from steps.conversion import GrayscaleConversionStep

def main():
    """A simple test script to verify the pipeline skeleton."""
    print("--- Starting Hello Pipeline Test ---")
    
    base_dir = os.path.dirname(__file__)
    input_image_path = os.path.join(base_dir, 'tests/data/sample_image.png')
    output_image_path = os.path.join(base_dir, 'tests/data/grayscale_output.png')
    
    print(f"Loading image from {input_image_path}...")
    if not os.path.exists(input_image_path):
        print(f"Error: Input image not found at {input_image_path}")
        return

    # 1. Load the sample image
    frame = cv2.imread(input_image_path)

    # 2. Create the pipeline with the single grayscale step
    pipeline = Pipeline(steps=[
        GrayscaleConversionStep()
    ])

    # 3. Create the initial builder
    builder = FrameContextBuilder(frame_index=0, original_frame=frame)

    # 4. Run the pipeline
    print("Running the pipeline...")
    processed_context = pipeline.run(builder)

    # 5. Get the result and save it
    grayscale_result = processed_context.grayscale_frame
    if grayscale_result is not None:
        print(f"Pipeline finished. Saving grayscale image to {output_image_path}...")
        cv2.imwrite(output_image_path, grayscale_result)
        print("\nSuccess! Check the grayscale_output.png file in tests/data/")
    else:
        print("Error: Grayscale image not found in the processed context.")
    
    print("--- Test Finished ---")

if __name__ == "__main__":
    main()
