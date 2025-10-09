import os
import argparse
from PIL import Image, ImageDraw, ImageFont

def create_montage(input_image_path, output_dir):
    """
    Creates a montage of original, HAWP detection, and L-CNN detection images.
    """
    print("--- Creating comparison montage ---")

    # Load images
    try:
        original_img = Image.open(input_image_path).convert("RGB")
        hawp_detection_img = Image.open(os.path.join(output_dir, "hawp_detection.png")).convert("RGB")
        lcnn_detection_img = Image.open(os.path.join(output_dir, "lcnn_detection.png")).convert("RGB")
    except FileNotFoundError as e:
        print(f"Error loading image: {e}. Ensure all detection images exist.")
        return
    except Exception as e:
        print(f"An error occurred while loading images: {e}")
        return

    # Resize all images to a common height for consistent display
    target_height = 512
    original_img = original_img.resize((int(original_img.width * target_height / original_img.height), target_height))
    hawp_detection_img = hawp_detection_img.resize((int(hawp_detection_img.width * target_height / hawp_detection_img.height), target_height))
    lcnn_detection_img = lcnn_detection_img.resize((int(lcnn_detection_img.width * target_height / lcnn_detection_img.height), target_height))

    # Create a new blank image for the montage
    total_width = original_img.width + hawp_detection_img.width + lcnn_detection_img.width
    max_height = target_height # All images are resized to this height
    
    montage = Image.new('RGB', (total_width, max_height), color = (255, 255, 255)) # White background

    # Paste images onto the montage
    x_offset = 0
    montage.paste(original_img, (x_offset, 0))
    x_offset += original_img.width
    montage.paste(hawp_detection_img, (x_offset, 0))
    x_offset += hawp_detection_img.width
    montage.paste(lcnn_detection_img, (x_offset, 0))

    # Add labels
    draw = ImageDraw.Draw(montage)
    try:
        font = ImageFont.truetype("arial.ttf", 30) # Try to use a common font
    except IOError:
        font = ImageFont.load_default() # Fallback to default font
    
    text_color = (0, 0, 0) # Black text

    # Labels for columns
    draw.text((original_img.width / 2 - 50, 10), "Original", font=font, fill=text_color)
    draw.text((original_img.width + hawp_detection_img.width / 2 - 50, 10), "HAWP Detection", font=font, fill=text_color)
    draw.text((original_img.width + hawp_detection_img.width + lcnn_detection_img.width / 2 - 50, 10), "L-CNN Detection", font=font, fill=text_color)

    # Save the montage
    montage_path = os.path.join(output_dir, "comparison_grid.png")
    montage.save(montage_path)
    print(f"Montage saved to {montage_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a montage of line detection results.")
    parser.add_argument("--input", type=str, required=True, help="Path to the original input image.")
    parser.add_argument("--dir", type=str, required=True, help="Path to the output directory containing detection images.")
    args = parser.parse_args()

    create_montage(args.input, args.dir)
