import cv2
import numpy as np

def find_contours(image_path: str) -> list:
    """
    Finds contours in a binary image.

    Args:
        image_path: Path to the input image file.

    Returns:
        A list of contours, where each contour is a list of points.
        Returns an empty list if the image cannot be read or no contours are found.
    """
    # Read the image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error: Image not found or could not be read at {image_path}")
        return []

    # Ensure it's a binary image (threshold if necessary)
    _, binary_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(binary_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return []

    # Squeeze contours to remove redundant dimensions and convert to list
    contours_as_lists = []
    for contour in contours:
        # Squeeze removes single-dimensional entries from the shape of an array.
        squeezed_contour = np.squeeze(contour, axis=1)
        contours_as_lists.append(squeezed_contour.tolist())

    return contours_as_lists

def visualize_contours(image_shape: tuple, contours: list, output_path: str):
    """
    Draws contours on a blank image for visualization.

    Args:
        image_shape: The shape (height, width, channels) of the original image.
        contours: A list of contours to draw.
        output_path: Path to save the visualization image.
    """
    # Create a blank black image with the same dimensions
    output_img = np.zeros(image_shape, dtype=np.uint8)

    # Prepare contours for drawing
    drawable_contours = [np.array(c, dtype=np.int32).reshape((-1, 1, 2)) for c in contours]

    # Draw contours
    cv2.drawContours(output_img, drawable_contours, -1, (0, 255, 0), 1)

    # Save the output image
    cv2.imwrite(output_path, output_img)
    print(f"Saved visualization to {output_path}")
