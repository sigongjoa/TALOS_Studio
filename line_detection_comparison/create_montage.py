import os
import argparse
from PIL import Image, ImageDraw, ImageFont

def create_montage(input_image_path, output_dir, models_to_include):
    """
    Creates a montage of original image and selected line detection results.
    """
    print("--- Creating comparison montage ---")

    # Map model names to their display labels and filenames
    model_map = {
        "sold2": {"label": "SOLD2 Detection", "filename": "sold2_detection.png"},
        "scalelsd": {"label": "ScaleLSD Detection", "filename": "scalelsd_detection.png"},
        "deeplsd": {"label": "DeepLSD Detection", "filename": "deeplsd_detection.png"},
        "manga_line_extraction": {"label": "MangaLineExtraction", "filename": "manga_line_extraction_detection.png"},
    }

    images_to_load = {}
    for model_name in models_to_include:
        if model_name in model_map:
            info = model_map[model_name]
            images_to_load[info["label"]] = info["filename"]

    loaded_images = {}

    # First, load the main input image
    try:
        loaded_images["Original (with info)"] = Image.open(input_image_path).convert("RGB")
    except FileNotFoundError:
        print(f"Warning: Could not find main input image {input_image_path}. Aborting.")
        return

    # Then, load the detection images from the output directory
    for label, filename in images_to_load.items():
        path = os.path.join(output_dir, filename)
        try:
            loaded_images[label] = Image.open(path).convert("RGB")
        except FileNotFoundError:
            print(f"Warning: Could not find image {path}. Skipping.")

    if not loaded_images:
        print("No images found to create a montage.")
        return

    # Resize all images to a common height for consistent display
    target_height = 512
    resized_images = []
    total_width = 0
    for label, img in loaded_images.items():
        resized_img = img.resize((int(img.width * target_height / img.height), target_height))
        resized_images.append((label, resized_img))
        total_width += resized_img.width

    # Create a new blank image for the montage
    max_height = target_height
    montage = Image.new('RGB', (total_width, max_height), color=(255, 255, 255)) # White background

    # Paste images onto the montage
    x_offset = 0
    for label, img in resized_images:
        montage.paste(img, (x_offset, 0))
        x_offset += img.width

    # Add labels
    draw = ImageDraw.Draw(montage)
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()
    
    text_color = (0, 0, 0) # Black text

    x_offset = 0
    for label, img in resized_images:
        bbox = draw.textbbox((0, 0), label, font=font)
        text_width = bbox[2] - bbox[0]
        draw.text((x_offset + img.width / 2 - text_width / 2, 10), label, font=font, fill=text_color)
        x_offset += img.width

    # Save the montage
    montage_path = os.path.join(output_dir, "comparison_grid.png")
    montage.save(montage_path)
    print(f"Montage saved to {montage_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a montage of line detection results.")
    parser.add_argument("--input", type=str, required=True, help="Path to the original input image.")
    parser.add_argument("--dir", type=str, required=True, help="Path to the output directory containing detection images.")
    parser.add_argument("--models", nargs='*', default=[], 
                        help="List of models to include in the montage (e.g., sold2 scalelsd deeplsd).")
    args = parser.parse_args()

    create_montage(args.input, args.dir, args.models)