
from PIL import Image
import os

def load_image(image_path: str) -> Image.Image:
    """
    Loads an image from the given file path.

    Args:
        image_path: The path to the image file.

    Returns:
        A PIL.Image.Image object.

    Raises:
        FileNotFoundError: If the image file does not exist at the given path.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"No such file or directory: '{image_path}'")
    
    # The 'with' statement is good practice as it handles closing the file.
    with Image.open(image_path) as img:
        # We need to load the image data to be able to use it after the 'with' block
        img.load()
        return img
