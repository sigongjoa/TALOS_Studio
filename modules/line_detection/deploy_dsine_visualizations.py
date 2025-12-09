import os
import shutil
import sys

def deploy_dsine_visualizations():
    dsine_output_path = "/mnt/d/progress/TALOS_Studio/line_detection_comparison/libs/DSINE/samples/output/"
    target_visualization_path = "/mnt/d/progress/TALOS_Studio/output_visualizations/dsine_output/"

    print(f"Attempting to copy visualizations from: {dsine_output_path}")
    print(f"To: {target_visualization_path}")

    if not os.path.exists(dsine_output_path):
        print(f"Error: DSINE output path not found at {dsine_output_path}")
        print("Please ensure you have run 'python /mnt/d/progress/TALOS_Studio/line_detection_comparison/run_dsine_minimal.py' successfully.")
        print("Also, make sure the DSINE model weights are downloaded as per the DSINE README.md.")
        sys.exit(1)

    # Create the target directory if it doesn't exist
    os.makedirs(target_visualization_path, exist_ok=True)

    # Copy contents of dsine_output_path to target_visualization_path
    for item in os.listdir(dsine_output_path):
        s = os.path.join(dsine_output_path, item)
        d = os.path.join(target_visualization_path, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

    print(f"Successfully copied DSINE visualizations to {target_visualization_path}")
    print("\n--- Next Steps for Deployment ---")
    print("1. Review the copied visualizations in the 'output_visualizations/dsine_output/' directory.")
    print("2. Stage your changes: 'git add .' ")
    print("3. Commit your changes with the '[publish]' keyword: 'git commit -m \"Feat: Add DSINE minimal test visualizations [publish]\"'")
    print("4. Push to the main branch: 'git push origin main'")
    print("This will trigger the GitHub Actions workflow to deploy your visualizations.")

if __name__ == "__main__":
    deploy_dsine_visualizations()
