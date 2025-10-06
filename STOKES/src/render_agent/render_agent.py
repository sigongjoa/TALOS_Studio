import os
import json
import subprocess
import matplotlib.pyplot as plt
import numpy as np

class RenderAgent:
    def __init__(self):
        """
        Initializes the RenderAgent.
        In a real scenario, this might involve setting up Blender or other rendering tools.
        """
        pass

    def render_vfx(self, simulation_data_path: str, output_dir: str = "outputs/temp_frames", video_filename: str = "vfx_output.mp4") -> str:
        """
        Renders VFX from simulation data and synthesizes it into a video.

        Args:
            simulation_data_path: The absolute path to the simulation data file (e.g., JSON).
            output_dir: The directory to save temporary frames and the final video.
            video_filename: The filename for the final video output.

        Returns:
            The absolute path to the generated video file.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"Rendering VFX from simulation data: {simulation_data_path}")

        # 1. Load simulation data
        try:
            with open(simulation_data_path, "r") as f:
                simulation_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading simulation data: {e}")
            return ""

        frames_data = simulation_data.get("frames", [])
        if not frames_data:
            print("No frames data found in simulation data.")
            return ""

        # 2. Generate matplotlib plots (frames)
        frame_paths = []
        for i, frame in enumerate(frames_data):
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Example: Plotting particles
            particles = frame.get("particles", [])
            if particles:
                x = [p["x"] for p in particles]
                y = [p["y"] for p in particles]
                ax.scatter(x, y, s=100, alpha=0.7)
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_title(f"Frame {frame.get('frame_number', i)} - Time: {frame.get('metadata', {}).get('time', 0):.2f}s")
            ax.set_aspect('equal', adjustable='box')
            
            frame_path = os.path.join(output_dir, f"frame_{i:04d}.png")
            plt.savefig(frame_path)
            plt.close(fig) # Close the figure to free memory
            frame_paths.append(frame_path)

        if not frame_paths:
            print("No frames were generated.")
            return ""

        # 3. Use ffmpeg to combine image files into a video
        final_video_path = os.path.join(output_dir, video_filename)
        
        # Ensure ffmpeg is available
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, text=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: ffmpeg not found. Please install ffmpeg to generate videos.")
            return ""

        # ffmpeg command to combine PNG frames into an MP4 video
        # -framerate: input frame rate
        # -i: input pattern (frame_%04d.png)
        # -c:v: video codec (libx264 is common)
        # -pix_fmt: pixel format (yuv420p for broad compatibility)
        # -y: overwrite output file if it exists
        # -r: output frame rate (e.g., 25 fps)
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",  # Overwrite output file without asking
            "-framerate", "10", # Input frame rate (10 frames per second)
            "-i", os.path.join(output_dir, "frame_%04d.png"),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "25", # Output frame rate (25 fps)
            final_video_path
        ]

        try:
            print(f"Running ffmpeg command: {' '.join(ffmpeg_cmd)}")
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
            print(f"Video generated successfully to: {final_video_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error during ffmpeg video generation: {e.stderr.decode()}")
            return ""
        except FileNotFoundError:
            print("Error: ffmpeg command not found. Please ensure ffmpeg is installed and in your PATH.")
            return ""
        
        # Clean up temporary frames
        for frame_path in frame_paths:
            os.remove(frame_path)
        
        return final_video_path