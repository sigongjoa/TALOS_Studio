import os
import shutil
import pytest
from generate_visualizations import generate_visualizations, INPUT_IMAGE_PATHS, OUTPUT_BASE_DIR

@pytest.fixture(scope="module")
def setup_teardown_output_dir():
    # Setup: Ensure output directory is clean before tests
    if os.path.exists(OUTPUT_BASE_DIR):
        shutil.rmtree(OUTPUT_BASE_DIR)
    os.makedirs(OUTPUT_BASE_DIR)
    yield
    # Teardown: Clean up output directory after tests
    if os.path.exists(OUTPUT_BASE_DIR):
        shutil.rmtree(OUTPUT_BASE_DIR)

def test_generate_visualizations_creates_files(setup_teardown_output_dir):
    # Run the main visualization generation function
    generate_visualizations()

    # Assert that the main output directory exists
    assert os.path.exists(OUTPUT_BASE_DIR)
    assert os.path.isdir(OUTPUT_BASE_DIR)

    # Assert that index.html is created
    index_html_path = os.path.join(OUTPUT_BASE_DIR, "index.html")
    assert os.path.exists(index_html_path)
    assert os.path.isfile(index_html_path)

    # Assert that subdirectories and image files are created for each input image
    expected_num_images = len(INPUT_IMAGE_PATHS)
    for i in range(expected_num_images):
        image_id = f"image_{i+1:02d}"
        output_sub_dir = os.path.join(OUTPUT_BASE_DIR, image_id)
        assert os.path.exists(output_sub_dir)
        assert os.path.isdir(output_sub_dir)

        # Check for the 5 expected image files
        expected_files = [
            "original.png",
            "manga_lines.png",
            "inverted_lines.png",
            "sold2_detection.png",
            "canny_detection.png",
        ]
        for filename in expected_files:
            file_path = os.path.join(output_sub_dir, filename)
            assert os.path.exists(file_path)
            assert os.path.isfile(file_path)

    # Optionally, check content of index.html for image references
    with open(index_html_path, "r") as f:
        html_content = f.read()
        for i in range(expected_num_images):
            image_id = f"image_{i+1:02d}"
            for filename in expected_files:
                # Check if the image src is present in the HTML content
                assert f'src="{image_id}/{filename}' in html_content
