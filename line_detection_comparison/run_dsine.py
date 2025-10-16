import os
import numpy as np
import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import sys

# Add the DSINE library to the python path
DSINE_PATH = os.path.join(os.path.dirname(__file__), 'libs', 'DSINE')
if DSINE_PATH not in sys.path:
    sys.path.append(DSINE_PATH)

from models.dsine.v02 import DSINE_v02 as DSINE
from utils import utils
from projects.dsine import config as dsine_config
from utils.projection import intrins_from_fov

# --- Globals for caching the model ---
_model = None

def get_dsine_model():
    """Loads and caches the DSINE model."""
    global _model
    if _model is None:
        print("Loading DSINE model for the first time...")
        # Correctly locate the checkpoint file relative to this script
        ckpt_path = os.path.join(DSINE_PATH, 'checkpoints', 'exp001_cvpr2024', 'dsine.pt')
        
        if not os.path.exists(ckpt_path):
            raise FileNotFoundError(f"DSINE model checkpoint not found at {ckpt_path}")

        args = dsine_config.get_args(test=True)
        args.ckpt_path = ckpt_path # Override with the correct path
        
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = DSINE(args).to(device)
        model = utils.load_checkpoint(args.ckpt_path, model)
        model.eval()
        _model = model
        print("DSINE model loaded successfully.")
    return _model

def run_dsine_inference(input_image_path, output_path):
    """
    Runs DSINE inference on a single image and saves the output normal map.
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = get_dsine_model()
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

    with torch.no_grad():
        img = Image.open(input_image_path).convert('RGB')
        img = np.array(img).astype(np.float32) / 255.0
        img = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0).to(device)

        # Pad input
        _, _, orig_H, orig_W = img.shape
        lrtb = utils.get_padding(orig_H, orig_W)
        img = F.pad(img, lrtb, mode="constant", value=0.0)
        img = normalize(img)

        # Get intrinsics (assuming 60-degree FOV as a default)
        intrins = intrins_from_fov(new_fov=60.0, H=orig_H, W=orig_W, device=device).unsqueeze(0)
        intrins[:, 0, 2] += lrtb[0]
        intrins[:, 1, 2] += lrtb[2]

        # Run model
        pred_norm = model(img, intrins=intrins)[-1]
        pred_norm = pred_norm[:, :, lrtb[2]:lrtb[2]+orig_H, lrtb[0]:lrtb[0]+orig_W]

        # Post-process and save
        pred_norm = pred_norm.detach().cpu().permute(0, 2, 3, 1).numpy()
        pred_norm_uint8 = (((pred_norm + 1) * 0.5) * 255).astype(np.uint8)
        
        im = Image.fromarray(pred_norm_uint8[0,...])
        im.save(output_path)
        print(f"Saved DSINE output to {output_path}")

if __name__ == '__main__':
    # Example usage for standalone testing
    # Ensure you have an image at the specified path
    input_img = os.path.join(os.path.dirname(__file__), '.._ref', 'image_01.jpg')
    output_img = os.path.join(os.path.dirname(__file__), '.._output', 'dsine_output_standalone.png')
    
    if not os.path.exists(os.path.dirname(output_img)):
        os.makedirs(os.path.dirname(output_img))

    if os.path.exists(input_img):
        run_dsine_inference(input_img, output_img)
    else:
        print(f"Input image not found at {input_img}, skipping standalone test.")