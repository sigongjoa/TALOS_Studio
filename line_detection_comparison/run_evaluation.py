#!/usr/bin/env python

import subprocess
import os
from PIL import Image, ImageDraw, ImageFont

# Define the project base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Input/Output Configuration ---
INPUT_IMAGE = os.path.join(BASE_DIR, "input", "test_image.jpg")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
INTERMEDIATE_IMAGE_PATH = os.path.join(OUTPUT_DIR, "intermediate_image.png")

def add_frame_info_to_image(input_path, output_path):
    """
    Adds a text block with the filename to the bottom of the image.
    """
    print(f"--- Adding frame info to {input_path} ---")
    try:
        img = Image.open(input_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()

        text = f"Source: {os.path.basename(input_path)}"
        text_color = (255, 255, 255) # White text
        
        # Create a black bar at the bottom
        bar_height = 30
        img_width, img_height = img.size
        new_img = Image.new('RGB', (img_width, img_height + bar_height), color=(0, 0, 0))
        new_img.paste(img, (0, 0))

        # Draw text on the black bar
        draw = ImageDraw.Draw(new_img)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_position = ((img_width - text_width) / 2, img_height + 5)
        draw.text(text_position, text, font=font, fill=text_color)

        new_img.save(output_path)
        print(f"--- Saved intermediate image to {output_path} ---")
        return True
    except Exception as e:
        print(f"Error adding frame info: {e}")
        return False

def run_evaluation_pipeline():
    """
    Main pipeline to run all evaluations.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Add frame info to the image first.
    print("--- Step 1: Adding frame info to image ---")
    if not add_frame_info_to_image(INPUT_IMAGE, INTERMEDIATE_IMAGE_PATH):
        print("Failed to create intermediate image. Aborting.")
        return

    # 2. Run individual model inference scripts using the intermediate image.
    print("\n--- Step 2: Running Model Inference ---")
    scripts_to_run = [
        os.path.join(BASE_DIR, "run_sold2.py"),
        os.path.join(BASE_DIR, "run_scalelsd.py"),
    ]

    for script in scripts_to_run:
        try:
            print(f"\n--- Executing {os.path.basename(script)} ---")
            subprocess.run(["python3", script], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running {script}: {e}")
            print(f"Stderr: {e.stderr}")

    # 3. Create the final montage with all the results.
    print("\n--- Step 3: Creating Final Montage ---")
    montage_script = os.path.join(BASE_DIR, "create_montage.py")
    try:
        subprocess.run(["python3", montage_script, "--input", INTERMEDIATE_IMAGE_PATH, "--dir", OUTPUT_DIR], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Montage creation failed: {e}")

    print("\n\nEvaluation pipeline finished.")

    print("\n\nEvaluation pipeline finished.")

if __name__ == "__main__":
    run_evaluation_pipeline()
