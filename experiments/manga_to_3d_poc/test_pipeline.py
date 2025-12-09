
import pytest
from PIL import Image
import os

# This import will fail initially, as we haven't created the function yet.
from pipeline import load_image

# Using an absolute path is important for tests to run from any directory.
VALID_IMAGE_PATH = os.path.abspath("ref/image_01.jpg")
INVALID_IMAGE_PATH = os.path.abspath("ref/non_existent_image.jpg")

def test_load_image_success():
    """
    Tests that load_image successfully loads an existing image.
    """
    assert os.path.exists(VALID_IMAGE_PATH), f"Test image not found at {VALID_IMAGE_PATH}"
    image = load_image(VALID_IMAGE_PATH)
    assert isinstance(image, Image.Image)

def test_load_image_not_found():
    """
    Tests that load_image raises FileNotFoundError for a non-existent path.
    """
    with pytest.raises(FileNotFoundError):
        load_image(INVALID_IMAGE_PATH)
