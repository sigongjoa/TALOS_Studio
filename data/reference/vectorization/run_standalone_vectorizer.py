import os
# --- Standalone Vectorization Pipeline ---
# This script combines all necessary functions to avoid python path issues.

import shutil
import numpy as np
import cv2
import torch
import vtracer
import torch.nn as nn

# --- 1. Model Definition (from run_manga_line_extraction.py) ---

class _bn_relu_conv(nn.Module):
    def __init__(self, in_filters, nb_filters, fw, fh, subsample=1):
        super(_bn_relu_conv, self).__init__()
        self.model = nn.Sequential(
            nn.BatchNorm2d(in_filters, eps=1e-3),
            nn.LeakyReLU(0.2),
            nn.Conv2d(in_filters, nb_filters, (fw, fh), stride=subsample, padding=(fw//2, fh//2), padding_mode='zeros')
        )
    def forward(self, x): return self.model(x)

class _u_bn_relu_conv(nn.Module):
    def __init__(self, in_filters, nb_filters, fw, fh, subsample=1):
        super(_u_bn_relu_conv, self).__init__()
        self.model = nn.Sequential(
            nn.BatchNorm2d(in_filters, eps=1e-3),
            nn.LeakyReLU(0.2),
            nn.Conv2d(in_filters, nb_filters, (fw, fh), stride=subsample, padding=(fw//2, fh//2)),
            nn.Upsample(scale_factor=2, mode='nearest')
        )
    def forward(self, x): return self.model(x)

class _shortcut(nn.Module):
    def __init__(self, in_filters, nb_filters, subsample=1):
        super(_shortcut, self).__init__()
        self.process = in_filters != nb_filters or subsample != 1
        if self.process:
            self.model = nn.Sequential(nn.Conv2d(in_filters, nb_filters, (1, 1), stride=subsample))
    def forward(self, x, y):
        return self.model(x) + y if self.process else x + y

class _u_shortcut(nn.Module):
    def __init__(self, in_filters, nb_filters, subsample):
        super(_u_shortcut, self).__init__()
        self.process = in_filters != nb_filters
        if self.process:
            self.model = nn.Sequential(
                nn.Conv2d(in_filters, nb_filters, (1, 1), stride=subsample, padding_mode='zeros'),
                nn.Upsample(scale_factor=2, mode='nearest')
            )
    def forward(self, x, y):
        return self.model(x) + y if self.process else x + y

class basic_block(nn.Module):
    def __init__(self, in_filters, nb_filters, init_subsample=1):
        super(basic_block, self).__init__()
        self.conv1 = _bn_relu_conv(in_filters, nb_filters, 3, 3, subsample=init_subsample)
        self.residual = _bn_relu_conv(nb_filters, nb_filters, 3, 3)
        self.shortcut = _shortcut(in_filters, nb_filters, subsample=init_subsample)
    def forward(self, x): return self.shortcut(x, self.residual(self.conv1(x)))

class _u_basic_block(nn.Module):
    def __init__(self, in_filters, nb_filters, init_subsample=1):
        super(_u_basic_block, self).__init__()
        self.conv1 = _u_bn_relu_conv(in_filters, nb_filters, 3, 3, subsample=init_subsample)
        self.residual = _bn_relu_conv(nb_filters, nb_filters, 3, 3)
        self.shortcut = _u_shortcut(in_filters, nb_filters, subsample=init_subsample)
    def forward(self, x): return self.shortcut(x, self.residual(self.conv1(x)))

class _residual_block(nn.Module):
    def __init__(self, in_filters, nb_filters, repetitions, is_first_layer=False):
        super(_residual_block, self).__init__()
        layers = []
        for i in range(repetitions):
            init_subsample = 2 if i == repetitions - 1 and not is_first_layer else 1
            l = basic_block(in_filters if i == 0 else nb_filters, nb_filters, init_subsample)
            layers.append(l)
        self.model = nn.Sequential(*layers)
    def forward(self, x): return self.model(x)

class _upsampling_residual_block(nn.Module):
    def __init__(self, in_filters, nb_filters, repetitions):
        super(_upsampling_residual_block, self).__init__()
        layers = []
        for i in range(repetitions):
            l = _u_basic_block(in_filters, nb_filters) if i == 0 else basic_block(nb_filters, nb_filters)
            layers.append(l)
        self.model = nn.Sequential(*layers)
    def forward(self, x): return self.model(x)

class res_skip(nn.Module):
    def __init__(self):
        super(res_skip, self).__init__()
        self.block0 = _residual_block(1, 24, 2, is_first_layer=True)
        self.block1 = _residual_block(24, 48, 3)
        self.block2 = _residual_block(48, 96, 5)
        self.block3 = _residual_block(96, 192, 7)
        self.block4 = _residual_block(192, 384, 12)
        self.block5 = _upsampling_residual_block(384, 192, 7)
        self.res1 = _shortcut(192, 192)
        self.block6 = _upsampling_residual_block(192, 96, 5)
        self.res2 = _shortcut(96, 96)
        self.block7 = _upsampling_residual_block(96, 48, 3)
        self.res3 = _shortcut(48, 48)
        self.block8 = _upsampling_residual_block(48, 24, 2)
        self.res4 = _shortcut(24, 24)
        self.block9 = _residual_block(24, 16, 2, is_first_layer=True)
        self.conv15 = _bn_relu_conv(16, 1, 1, 1)
    def forward(self, x):
        x0 = self.block0(x)
        x1 = self.block1(x0)
        x2 = self.block2(x1)
        x3 = self.block3(x2)
        x4 = self.block4(x3)
        x5 = self.block5(x4)
        res1 = self.res1(x3, x5)
        x6 = self.block6(res1)
        res2 = self.res2(x2, x6)
        x7 = self.block7(res2)
        res3 = self.res3(x1, x7)
        x8 = self.block8(res3)
        res4 = self.res4(x0, x8)
        x9 = self.block9(res4)
        return self.conv15(x9)

def run_manga_line_extraction_inference(input_image_path, output_image_path):
    model = res_skip()
    weights_path = 'line_detection_comparison/libs/MangaLineExtraction_PyTorch/erika.pth'
    model.load_state_dict(torch.load(weights_path, map_location=torch.device('cpu')))
    model.eval()
    src = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
    if src is None: return
    rows, cols = int(np.ceil(src.shape[0]/16))*16, int(np.ceil(src.shape[1]/16))*16
    patch = np.ones((1,1,rows,cols), dtype="float32")
    patch[0,0,0:src.shape[0],0:src.shape[1]] = src
    with torch.no_grad():
        y = model(torch.from_numpy(patch).cpu())
    yc = y.cpu().numpy()[0,0,:,:]
    yc[yc>255], yc[yc<0] = 255, 0
    cv2.imwrite(output_image_path, yc[0:src.shape[0],0:src.shape[1]])

# --- 2. HTML Generation Function ---
def create_visualization_html(output_dir, image_dirs):
    """Generates the final index.html to display all results."""
    html_content = """
    <!DOCTYPE html>
    <html lang="en"><head>
    <meta charset="utf-8"/>
    <title>Vectorization Showcase</title>
    <script src="https://cdn.tailwindcss.com?plugins=forms,typography"></script>
    </head>
    <body class="bg-gray-100">
    <div class="container mx-auto px-4 py-8">
    <h1 class="text-4xl font-bold text-center mb-8">Image Vectorization Showcase</h1>
    """

    for img_dir in sorted(image_dirs):
        base_name = os.path.basename(img_dir)
        html_content += f'''
        <div class="bg-white p-6 rounded-lg shadow-lg mb-8">
            <h2 class="text-2xl font-bold mb-4">{base_name}</h2>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                <div>
                    <h3 class="font-semibold">1. Original</h3>
                    <img src="{base_name}/original.png" alt="Original" class="inline-block w-full h-auto border"/>
                </div>
                <div>
                    <h3 class="font-semibold">2. Line Art (Input)</h3>
                    <img src="{base_name}/line_art.png" alt="Line Art" class="inline-block w-full h-auto border"/>
                </div>
                <div>
                    <h3 class="font-semibold">3. Final Vector (SVG)</h3>
                    <img src="{base_name}/vector.svg" alt="Vector SVG" class="inline-block w-full h-auto border"/>
                </div>
            </div>
        </div>
        '''

    html_content += "</div></body></html>"

    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(html_content)

# --- 3. Main Pipeline Logic ---
def main():
    INPUT_DIR = "ref"
    OUTPUT_DIR = "output_visualizations"
    if os.path.exists(OUTPUT_DIR): shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    image_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
    processed_image_dirs = []
    for image_file in image_files:
        print(f"--- Processing {image_file} ---")
        base_name = os.path.splitext(image_file)[0]
        image_output_dir = os.path.join(OUTPUT_DIR, base_name)
        os.makedirs(image_output_dir, exist_ok=True)
        processed_image_dirs.append(base_name)
        original_img_path = os.path.join(INPUT_DIR, image_file)
        line_art_path = os.path.join(image_output_dir, "line_art.png")
        shutil.copy(original_img_path, os.path.join(image_output_dir, "original.png"))
        input_image = cv2.imread(original_img_path)
        h, w, _ = input_image.shape
        print("Step 1: Extracting Lines...")
        run_manga_line_extraction_inference(original_img_path, line_art_path)
        print("Step 2: Vectorizing with VTracer...")
        svg_path = os.path.join(image_output_dir, "vector.svg")
        # VTracer can take the input path and output path directly
        vtracer.convert_image_to_svg_py(line_art_path, svg_path)

        print(f"Step 3: Saving results...")
        print(f"Saved SVG to {svg_path}")
    print("Step 4: Creating showcase HTML...")
    # I need to re-insert the full HTML generation logic here.
    # For brevity in this thought, I'll just call a placeholder.
    create_visualization_html(OUTPUT_DIR, processed_image_dirs)
    print("\nShowcase generation complete!")

if __name__ == "__main__":
    main()
