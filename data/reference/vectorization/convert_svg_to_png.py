import argparse
import cairosvg
import os

def convert_svg_to_png(svg_path: str, png_path: str):
    """Converts an SVG file to a PNG file."""
    if not os.path.exists(svg_path):
        print(f"Error: Input SVG file not found at {svg_path}")
        return

    print(f"Converting {svg_path} to {png_path}...")
    cairosvg.svg2png(url=svg_path, write_to=png_path)
    print("Conversion successful.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert an SVG file to a PNG file.")
    parser.add_argument("input_svg", help="Path to the input SVG file.")
    parser.add_argument("output_png", help="Path to save the output PNG file.")
    args = parser.parse_args()

    convert_svg_to_png(args.input_svg, args.output_png)
