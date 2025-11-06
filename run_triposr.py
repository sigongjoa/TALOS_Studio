import argparse
import logging
import os
import time
import sys

# Add the TripoSR directory to sys.path to ensure the tsr module is found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'line_detection_comparison/TripoSR')))

import numpy as np
import rembg
import torch
from PIL import Image

# Assuming TripoSR is installed in the environment and its modules are accessible
from tsr.system import TSR
from tsr.utils import remove_background, resize_foreground


class Timer:
    def __init__(self):
        self.items = {}
        self.time_scale = 1000.0  # ms
        self.time_unit = "ms"

    def start(self, name: str) -> None:
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        self.items[name] = time.time()
        logging.info(f"{name} ...")

    def end(self, name: str) -> float:
        if name not in self.items:
            return
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        start_time = self.items.pop(name)
        delta = time.time() - start_time
        t = delta * self.time_scale
        logging.info(f"{name} finished in {t:.2f}{self.time_unit}.")


timer = Timer()


logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
parser = argparse.ArgumentParser()
parser.add_argument("--input_image", type=str, required=True, help="Path to input image.")
parser.add_argument(
    "--output_dir",
    default="output/",
    type=str,
    help="Output directory to save the results. Default: 'output/'",
)
parser.add_argument(
    "--device",
    default="cuda:0",
    type=str,
    help="Device to use. If no CUDA-compatible device is found, will fallback to 'cpu'. Default: 'cuda:0'",
)
parser.add_argument(
    "--pretrained_model_name_or_path",
    default="stabilityai/TripoSR",
    type=str,
    help="Path to the pretrained model. Could be either a huggingface model id is or a local path. Default: 'stabilityai/TripoSR'",
)
parser.add_argument(
    "--model_save_format",
    default="obj",
    type=str,
    choices=["obj", "glb"],
    help="Format to save the extracted mesh. Default: 'obj'",
)
parser.add_argument(
    "--no_remove_bg",
    action="store_true",
    help="If specified, the background will NOT be automatically removed from the input image, and the input image should be an RGB image with gray background and properly-sized foreground. Default: false",
)
parser.add_argument(
    "--foreground_ratio",
    default=0.85,
    type=float,
    help="Ratio of the foreground size to the image size. Only used when --no-remove-bg is not specified. Default: 0.85",
)


parser.add_argument(
    "--chunk_size",
    default=8192,
    type=int,
    help="Evaluation chunk size. Smaller values reduce VRAM usage.",
)


args = parser.parse_args()

output_dir = args.output_dir
os.makedirs(output_dir, exist_ok=True)

device = args.device
if not torch.cuda.is_available():
    device = "cpu"

timer.start("Initializing model")
model = TSR.from_pretrained(
    args.pretrained_model_name_or_path,
    config_name="config.yaml",
    weight_name="model.ckpt",
)
model.renderer.set_chunk_size(args.chunk_size)
model.to(device)
timer.end("Initializing model")

timer.start("Processing image")
if args.no_remove_bg:
    rembg_session = None
else:
    rembg_session = rembg.new_session()

image = Image.open(args.input_image).convert("RGB")
if not args.no_remove_bg:
    image = remove_background(image, rembg_session)
    image = resize_foreground(image, args.foreground_ratio)
    image = np.array(image).astype(np.float32) / 255.0
    image = image[:, :, :3] * image[:, :, 3:4] + (1 - image[:, :, 3:4]) * 0.5
    image = Image.fromarray((image * 255.0).astype(np.uint8))

images = [image] # TripoSR expects a list of images
timer.end("Processing image")

timer.start("Running model")
with torch.no_grad():
    scene_codes = model(images, device=device)
timer.end("Running model")

timer.start("Extracting mesh")
# TripoSR's run.py uses bake_texture argument for extract_mesh, but our simplified script doesn't have it.
# Assuming we don't bake texture for now, or it's handled by default in extract_mesh
meshes = model.extract_mesh(scene_codes, False) # False for not baking texture
timer.end("Extracting mesh")

out_mesh_path = os.path.join(output_dir, f"model.{args.model_save_format}")
timer.start("Exporting mesh")
meshes[0].export(out_mesh_path)
timer.end("Exporting mesh")
