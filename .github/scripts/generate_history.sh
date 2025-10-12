#!/bin/bash

# Exit on error and print commands
set -ex

OUTPUT_DIR="output_for_deployment"

# Create a clean output directory
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# Create a very simple index.html file
echo "<h1>Hello World</h1><p>Updated at: $(date -u)</p>" > "$OUTPUT_DIR/index.html"

echo "Minimal index.html created successfully."
