
import os
import sys
import glob
import torch
from PIL import Image
from torchvision.transforms import ToTensor

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.append(PROJECT_ROOT)

from line_detection_comparison.libs.DSINE.hubconf import DSINE

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(os.path.dirname(BASE_DIR), "ref")
OUTPUT_DIR = os.path.join(os.path.dirname(BASE_DIR), "output_visualizations")
MODEL_WEIGHTS_PATH = os.path.join(BASE_DIR, "models/DSINE/checkpoints/exp001_cvpr2024/dsine.pt")

# --- Model Loading ---
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_predictor = DSINE(local_file_path=MODEL_WEIGHTS_PATH)
model = model_predictor.model.to(device) # Access the underlying model from the Predictor
model.eval()
print(f"DSINE model loaded from {MODEL_WEIGHTS_PATH} on {device}.")
