import os
import shutil
import json
import datetime
import glob

# Define the project base directory and paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DEPLOYMENT_DIR = os.path.join(BASE_DIR, "..", "output_for_deployment")

def get_source_image_path():
    """Finds the source image used for the detections."""
    for ext in ["*.jpg", "*.jpeg", "*.png"]:
        images = glob.glob(os.path.join(INPUT_DIR, ext))
        if images:
            return images[0]
    return None

def package_for_deployment():
    """
    Finds all model outputs in the 'output' directory, and creates a 
    separate, timestamped deployment page for each one.
    """
    print("--- Packaging Individual Model Results for Deployment ---")

    source_image_path = get_source_image_path()
    if not source_image_path:
        print("Error: Could not find a source image in the 'input' directory.")
        return

    source_image_name = os.path.basename(source_image_path)
    print(f"Using source image: {source_image_name}")

    detection_files = glob.glob(os.path.join(OUTPUT_DIR, "*_detection.png"))
    if not detection_files:
        print("No '*_detection.png' files found. Nothing to deploy.")
        return

    # --- Load pages.json once ---
    pages_json_path = os.path.join(DEPLOYMENT_DIR, "pages.json")
    pages = []
    if os.path.exists(pages_json_path):
        try:
            with open(pages_json_path, "r") as f:
                pages = json.load(f)
        except json.JSONDecodeError:
            pages = []

    # --- Process Each Model Detection File ---
    for f_path in sorted(detection_files):
        f_name = os.path.basename(f_path)
        model_name = f_name.replace("_detection.png", "")
        
        print(f"\nProcessing model: {model_name.upper()}")

        # --- 1. Create Page Directory ---
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        page_dir_name = f"{model_name}-{timestamp}"
        page_dir_path = os.path.join(DEPLOYMENT_DIR, page_dir_name)
        os.makedirs(page_dir_path, exist_ok=True)

        # --- 2. Copy Files & Handle Metadata ---
        # Copy original image
        shutil.copy(source_image_path, os.path.join(page_dir_path, "original.png"))
        # Copy detection image
        shutil.copy(f_path, os.path.join(page_dir_path, "detection.png"))

        # Check for and copy JSON metadata
        json_metadata_path = f_path.replace(".png", ".json")
        metadata_content = ""
        if os.path.exists(json_metadata_path):
            shutil.copy(json_metadata_path, os.path.join(page_dir_path, "metadata.json"))
            metadata_content = '<div class="metadata"><a href="metadata.json" download>Download Metadata (JSON)</a></div>'
            print(f"  - Found and copied metadata: {os.path.basename(json_metadata_path)}")

        # --- 3. Generate HTML ---
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detection Result</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 font-sans p-8">
    <header class="text-center mb-12">
        <h1 id="page-title" class="text-4xl font-bold"></h1>
        <p id="page-description" class="text-lg text-slate-600"></p>
    </header>
    <main class="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
        <div class="card"><h2>Original</h2><img src="original.png" alt="Original"></div>
        <div class="card"><h2>Detection</h2><img src="detection.png" alt="Detection"></div>
    </main>
    <footer class="text-center mt-8">{metadata_content}</footer>
    <style>
        .card {{ background-color: #fff; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); overflow: hidden; }}
        .card h2 {{ font-size: 1.1em; font-weight: 600; padding: 0.8em 1em; margin: 0; border-bottom: 1px solid #e9ecef; background-color: #f8f9fa; }}
        .metadata a {{ background-color: #334155; color: white; padding: 0.5em 1em; border-radius: 5px; text-decoration: none; }}
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            // Path of the current page relative to the deployment root
            const currentPagePath = `./{page_dir_name}/`;

            fetch('../pages.json')
                .then(response => response.json())
                .then(pages => {{
                    const pageInfo = pages.find(p => p.path === currentPagePath);
                    if (pageInfo) {{
                        document.getElementById('page-title').textContent = pageInfo.title || 'Detection Result';
                        document.getElementById('page-description').textContent = pageInfo.description || '';
                        document.title = pageInfo.title || 'Detection Result';
                    }}
                }})
                .catch(error => console.error('Error fetching pages.json:', error));
        }});
    </script>
</body>
</html>
"""
        with open(os.path.join(page_dir_path, "index.html"), "w") as f:
            f.write(html_content)
        print(f"  - Generated page at: {page_dir_path}")

        # --- 4. Update pages.json Entry ---
        new_page_entry = {
            "title": f"{model_name.upper()} Detection",
            "description": f"Source: {source_image_name} | Updated: {timestamp}",
            "path": f"./{page_dir_name}/"
        }
        # Remove old entry for this model to avoid duplicates
        pages = [p for p in pages if not p.get('title', '').startswith(f"{model_name.upper()} Detection")]
        pages.insert(0, new_page_entry)

    # --- Write pages.json once at the end ---
    with open(pages_json_path, "w") as f:
        json.dump(pages, f, indent=2)
    
    print(f"\nSuccessfully updated {pages_json_path}")

if __name__ == "__main__":
    package_for_deployment()