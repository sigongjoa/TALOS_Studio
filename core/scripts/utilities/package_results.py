
import os
import json
import argparse
from datetime import datetime

def create_html_content(model_dir_name, obj_file, input_image, rendered_images):
    # Paths should be relative to the HTML file's location
    relative_obj_path = obj_file
    relative_input_image = input_image
    relative_rendered_images = rendered_images

    rendered_images_html = ""
    for img in relative_rendered_images:
        rendered_images_html += f'<img src="{img}" width="200" style="margin: 10px;">'

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Model Showcase: {model_dir_name}</title>
    <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.5.0/model-viewer.min.js"></script>
    <style>
        body {{ font-family: sans-serif; margin: 2em; }}
        #viewer-container {{
            width: 80%;
            height: 600px;
            margin: 0 auto;
            border: 1px solid #ccc;
        }}
        h1, h2 {{ text-align: center; }}
        .image-gallery {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <h1>3D Model Showcase: {model_dir_name}</h1>

    <h2>Interactive 3D Model</h2>
    <div id="viewer-container">
        <model-viewer src="{relative_obj_path}"
                      alt="A 3D model of {model_dir_name}"
                      ar
                      ar-modes="webxr scene-viewer quick-look"
                      camera-controls
                      poster="poster.webp"
                      shadow-intensity="1"
                      environment-image="neutral"
                      auto-rotate>
        </model-viewer>
    </div>

    <h2>Original Input Image</h2>
    <div style="text-align: center; margin-top: 20px;">
        <img src="{relative_input_image}" width="400">
    </div>

    <h2>Rendered Views</h2>
    <div class="image-gallery">
        {rendered_images_html}
    </div>

</body>
</html>
"""
    return html_content

def main():
    parser = argparse.ArgumentParser(description="Package 3D model results for web deployment.")
    parser.add_argument("result_dir", type=str, help="Directory containing the model, input image, and rendered views.")
    args = parser.parse_args()

    result_dir = args.result_dir
    if not os.path.isdir(result_dir):
        print(f"Error: Directory not found at {result_dir}")
        return

    # Find the necessary files
    obj_file = None
    input_image = None
    rendered_images = []

    for item in sorted(os.listdir(os.path.join(result_dir, '0'))):
        if item.endswith(".obj"):
            obj_file = os.path.join('0', item)
        elif item == "input.png":
            input_image = os.path.join('0', item)
        elif item.startswith("render_") and item.endswith(".png"):
            rendered_images.append(os.path.join('0', item))

    if not obj_file:
        print("Error: No .obj file found in the result directory.")
        return

    # Create the HTML file
    model_dir_name = os.path.basename(result_dir)
    html_content = create_html_content(model_dir_name, obj_file, input_image, rendered_images)
    html_file_path = os.path.join(result_dir, "index.html")
    with open(html_file_path, "w") as f:
        f.write(html_content)
    print(f"Successfully created HTML file at {html_file_path}")

    # Update pages.json
    pages_json_path = "output_for_deployment/pages.json"
    pages_data = []
    if os.path.exists(pages_json_path):
        with open(pages_json_path, "r") as f:
            try:
                pages_data = json.load(f)
            except json.JSONDecodeError:
                pages_data = [] # Reset if file is corrupted

    new_entry = {
        "title": f"TripoSR: {model_dir_name}",
        "path": f"{model_dir_name}/index.html",
        "date": datetime.now().strftime("%Y-%m-%d")
    }

    # Avoid duplicate entries
    if not any(d['path'] == new_entry['path'] for d in pages_data):
        pages_data.append(new_entry)

    with open(pages_json_path, "w") as f:
        json.dump(pages_data, f, indent=4)
    print(f"Successfully updated {pages_json_path}")

if __name__ == "__main__":
    main()
