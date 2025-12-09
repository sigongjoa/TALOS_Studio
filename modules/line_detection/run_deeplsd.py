import os
import numpy as np
import cv2
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from deeplsd.utils.tensor import batch_to_device
from deeplsd.models.deeplsd import DeepLSD
from deeplsd.geometry.viz_2d import plot_images, plot_lines

def run_deeplsd_inference(input_image_path, output_image_path):
    # Load an image
    img = cv2.imread(input_image_path)[:, :, ::-1]
    gray_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    # Model config
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    conf = {
        'sharpen': True,  # Use the DF normalization (should be True)
        'detect_lines': True,  # Whether to detect lines or only DF/AF
        'line_detection_params': {
            'merge': False,  # Whether to merge close-by lines
            'optimize': False,  # Whether to refine the lines after detecting them
            'use_vps': True,  # Whether to use vanishing points (VPs) in the refinement
            'optimize_vps': True,  # Whether to also refine the VPs in the refinement
            'filtering': True,  # Whether to filter out lines based on the DF/AF. Use 'strict' to get an even stricter filtering
            'grad_thresh': 3,
            'grad_nfa': True,  # If True, use the image gradient and the NFA score of LSD to further threshold lines. We recommand using it for easy images, but to turn it off for challenging images (e.g. night, foggy, blurry images)
        }
    }

    # Load the model
    # Adjust the path to the model checkpoint
    script_dir = os.path.dirname(__file__)
    ckpt_path = os.path.join(script_dir, 'libs', 'DeepLSD', 'weights', 'deeplsd_md.tar')
    
    ckpt = torch.load(str(ckpt_path), map_location='cpu')
    net = DeepLSD(conf)
    net.load_state_dict(ckpt['model'])
    net = net.to(device).eval()

    # Detect (and optionally refine) the lines
    inputs = {'image': torch.tensor(gray_img, dtype=torch.float, device=device)[None, None] / 255.}
    with torch.no_grad():
        out = net(inputs)
        pred_lines = out['lines'][0]

    # Plot the predictions and save to file
    fig, ax = plot_images([img], ['DeepLSD lines'], cmaps='gray')
    plot_lines([pred_lines], indices=range(1), ax=ax[0])
    plt.savefig(output_image_path)
    plt.close(fig)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run DeepLSD inference on an image.")
    parser.add_argument("--input_image", type=str, required=True, help="Path to the input image.")
    parser.add_argument("--output_image", type=str, required=True, help="Path to save the output image with detected lines.")
    args = parser.parse_args()

    run_deeplsd_inference(args.input_image, args.output_image)