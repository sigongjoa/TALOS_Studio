from PIL import Image # Ensure Image is imported first
import os
import sys
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import numpy as np
import torch
import torchvision.transforms.functional as functional # Moved here
import cv2
import matplotlib.pyplot as plt
import torch.nn.functional as F

# Add LETR library path to sys.path for relative imports
LETR_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "libs", "LETR", "src"))
if LETR_PATH not in sys.path:
    sys.path.insert(0, LETR_PATH)

# Import from LETR's models and util
from models import build_model
from util.misc import nested_tensor_from_tensor_list

# --- Data Transforms (Copied from demo_letr.ipynb) ---
class Compose(object):
    def __init__(self, transforms):
        self.transforms = transforms

    def __call__(self, image):
        for t in self.transforms:
            image = t(image)
        return image

    def __repr__(self):
        format_string = self.__class__.__name__ + "("
        for t in self.transforms:
            format_string += "\n"
            format_string += "    {0}".format(t)
        format_string += "\n)"
        return format_string

class Normalize(object):
    def __init__(self, mean, std):
        self.mean = mean
        self.std = std

    def __call__(self, image):
        image = functional.normalize(image, mean=self.mean, std=self.std)
        return image

class ToTensor(object):
    def __call__(self, img):
        return functional.to_tensor(img)

def resize(image, size, max_size=None):
    def get_size_with_aspect_ratio(image_size, size, max_size=None):
        w, h = image_size
        if max_size is not None:
            min_original_size = float(min((w, h)))
            max_original_size = float(max((w, h)))
            if max_original_size / min_original_size * size > max_size:
                size = int(round(max_size * min_original_size / max_original_size))
        if (w <= h and w == size) or (h <= w and h == size):
            return (h, w)
        if w < h:
            ow = size
            oh = int(size * h / w)
        else:
            oh = size
            ow = int(size * w / h)
        return (oh, ow)

    def get_size(image_size, size, max_size=None):
        if isinstance(size, (list, tuple)):
            return size[::-1]
        else:
            return get_size_with_aspect_ratio(image_size, size, max_size)

    size = get_size(image.size, size, max_size)
    rescaled_image = functional.resize(image, size)
    return rescaled_image

class Resize(object):
    def __init__(self, sizes, max_size=None):
        assert isinstance(sizes, (list, tuple))
        self.sizes = sizes
        self.max_size = max_size

    def __call__(self, img):
        size = self.sizes
        return resize(img, size, self.max_size)

# --- Main Inference Function ---
def run_letr(input_image_path, output_dir):
    print("--- Running LETR (Wireframe Transformer) Inference ---")

    # Define checkpoint path relative to this script
    LETR_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "libs", "LETR"))
    CHECKPOINT_PATH = os.path.join(LETR_BASE_DIR, "checkpoints", "exp", "res101_stage2_focal", "checkpoints", "checkpoint0024.pth")

    if not os.path.exists(CHECKPOINT_PATH):
        print(f"Error: Checkpoint not found at {CHECKPOINT_PATH}")
        print("Please ensure the checkpoint is downloaded and unzipped correctly.")
        return

    # Load model pre-trained weights
    checkpoint = torch.load(CHECKPOINT_PATH, map_location='cpu')
    args = checkpoint['args']
    args.device = 'cpu' # Force device to CPU
    model, _, postprocessors = build_model(args)
    model.load_state_dict(checkpoint['model'])
    model.to('cpu') # Move model to CPU
    model.eval()

    # Load image
    raw_img_pil = Image.open(input_image_path).convert("RGB")
    h, w = raw_img_pil.size[1], raw_img_pil.size[0] # PIL.Image.size is (width, height)
    orig_size = torch.as_tensor([int(h), int(w)])

    # Normalize image
    test_size = 1100
    normalize = Compose([
            ToTensor(),
            Normalize([0.538, 0.494, 0.453], [0.257, 0.263, 0.273]),
            Resize([test_size]),
        ])
    img = normalize(raw_img_pil)
    inputs = nested_tensor_from_tensor_list([img])

    # Model Inference
    with torch.no_grad():
        outputs = model(inputs)[0]

    # Post-processing Results
    out_logits, out_line = outputs['pred_logits'], outputs['pred_lines']
    prob = F.softmax(out_logits, -1)
    scores, labels = prob[..., :-1].max(-1)
    img_h, img_w = orig_size.unbind(0)
    scale_fct = torch.unsqueeze(torch.stack([img_w, img_h, img_w, img_h], dim=0), dim=0)
    lines = out_line * scale_fct[:, None, :]
    lines = lines.view(1000, 2, 2)
    lines = lines.flip([-1]) # this is yxyx format
    scores = scores.detach().numpy()
    keep = scores >= 0.7
    keep = keep.squeeze()
    lines = lines[keep]

    # Handle case where no lines are detected
    if lines.shape[0] == 0:
        print("No lines detected with score >= 0.7. Skipping line plotting.")
        lines = np.array([]) # Ensure lines is an empty numpy array for consistent handling
    else:
        lines = lines.reshape(lines.shape[0], -1)

    # Plot and Save Results
    output_image_path = os.path.join(output_dir, "letr_detection.png")
    
    fig = plt.figure(frameon=False)
    ax = plt.Axes(fig, [0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    ax.imshow(raw_img_pil) # Use PIL image for imshow

    for tp_id, line in enumerate(lines):
        y1, x1, y2, x2 = line # this is yxyx
        p1 = (x1, y1)
        p2 = (x2, y2)
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], linewidth=1.5, color='darkorange', zorder=1)
    
    plt.savefig(output_image_path, dpi=300, bbox_inches='tight', pad_inches = 0)
    plt.close(fig)
    print(f"--- LETR Inference Complete. Output saved to {output_image_path} ---")

if __name__ == "__main__":
    # Define default paths for standalone testing
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DEFAULT_INPUT_IMAGE = os.path.join(BASE_DIR, "input", "test_image.jpg")
    DEFAULT_OUTPUT_DIR = os.path.join(BASE_DIR, "output")
    os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

    run_letr(DEFAULT_INPUT_IMAGE, DEFAULT_OUTPUT_DIR)
    print("\nLETR script finished.")