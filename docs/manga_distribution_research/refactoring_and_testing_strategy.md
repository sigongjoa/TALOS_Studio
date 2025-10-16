# Local Build and Pre-built Deployment Strategy

This document outlines the development and deployment workflow for this project. The core concept is a **pre-built deployment strategy**, where visualization results are generated locally and then committed to the repository for the CI/CD pipeline to deploy.

## 1. Core Concept: Pre-built Deployment

The CI/CD pipeline's role is **only to deploy**. It does **not** build, test, or generate any files. All visualization assets (HTML, images) must be generated on a developer's local machine, added to Git, and then pushed. This makes the CI/CD process fast and simple, as it only needs to take the pre-built files and publish them to GitHub Pages.

## 2. Developer's Local Workflow

To update the deployed website with new visualization results, follow these steps on your local machine.

### Step 1: Set Up Local Environment

Ensure your local virtual environment is set up and all dependencies are installed.

- **Virtual Environment Location:** `line_detection_comparison/venv/`
- **Activation:**
  ```bash
  source /mnt/d/progress/TALOS_Studio/line_detection_comparison/venv/bin/activate
  ```
- **Dependency Installation:**
  Install all necessary packages. The `SOLD2` requirements file is a good starting point.
  ```bash
  pip install -r line_detection_comparison/libs/SOLD2/requirements.txt
  ```

### Step 2: Generate Visualization Results

Run the main visualization script. This will execute all configured models (like `SOLD2` and `DSINE`) and place the results in the `output_visualizations` directory.

```bash
python generate_visualizations.py
```

*(You can also run `pytest` to generate the results, but be aware that the test environment is configured to clean up the output directory after the run.)*

### Step 3: Prepare Files for Deployment

The deployment script looks for assets in the `output_for_deployment` directory. You must copy your new results into this directory.

```bash
# Remove the old deployment files
rm -rf ./output_for_deployment/*

# Copy the new results from output_visualizations to output_for_deployment
mv ./output_visualizations/* ./output_for_deployment/
```

**Important:** Ensure the `output_for_deployment` directory contains the `index.html` and the `image_01`, `image_02`, etc. subdirectories before proceeding.

### Step 4: Commit and Push the Results

Add all changes, including the newly copied files in `output_for_deployment`, to Git and push them to the repository.

```bash
# Add all source code and the new deployment files
git add .

# Commit the changes
git commit -m "feat: Update visualization results with new DSINE output"

# Push to the remote repository
git push
```

## 3. CI/CD Workflow (`deploy.yml`)

Once you push your commit, the CI/CD workflow will automatically handle the rest.

1.  **Trigger:** The workflow starts on a push to the `main` or `master` branch.
2.  **Checkout:** It checks out the repository, which now includes your committed, pre-built files in `output_for_deployment`.
3.  **Prepare & Deploy:** It runs the `generate_history.sh` script. This script takes the content from your `output_for_deployment` folder, archives it, updates the main `index.html` history log, and pushes the final result to the `gh-pages` branch for deployment.

This process ensures that what you build and test locally is exactly what gets deployed.