import os
import subprocess
from src.style_agent.style_agent import StyleAgent
from src.narration_agent.narration_agent import NarrationAgent
from src.simulation_agent.simulation_agent import SimulationAgent
from src.render_agent.render_agent import RenderAgent

class Orchestrator:
    def __init__(self, style_agent: StyleAgent, narration_agent: NarrationAgent, simulation_agent: SimulationAgent, render_agent: RenderAgent):
        """
        Initializes the Orchestrator with instances of all agents.
        """
        self.style_agent = style_agent
        self.narration_agent = narration_agent
        self.simulation_agent = simulation_agent
        self.render_agent = render_agent

    def run_pipeline(self, user_input: str, output_base_dir: str = "outputs/final_shorts") -> str:
        """
        Runs the entire pipeline from user input to final short video.

        Args:
            user_input: The natural language description from the user.
            output_base_dir: The base directory to save all generated outputs.

        Returns:
            The absolute path to the final synthesized short video.
        """
        os.makedirs(output_base_dir, exist_ok=True)
        
        # 1. StyleAgent: Extract parameters and formulas
        print("Orchestrator: Running StyleAgent...")
        extracted_parameters, extracted_formula = self.style_agent.extract_parameters_and_formulas(user_input)
        print(f"Orchestrator: StyleAgent extracted parameters: {extracted_parameters}, formula: {extracted_formula}")

        # 2. NarrationAgent: Generate narration audio and subtitles
        print("Orchestrator: Running NarrationAgent...")
        narration_output_dir = os.path.join(output_base_dir, "narration")
        audio_path, subtitle_path = self.narration_agent.process_narration(extracted_formula, extracted_parameters, narration_output_dir)
        print(f"Orchestrator: NarrationAgent generated audio: {audio_path}, subtitles: {subtitle_path}")

        # 3. SimulationAgent: Run fluid simulation
        print("Orchestrator: Running SimulationAgent...")
        simulation_output_dir = os.path.join(output_base_dir, "fluid_data")
        simulation_data_path = self.simulation_agent.run_simulation(extracted_parameters, extracted_formula, simulation_output_dir)
        print(f"Orchestrator: SimulationAgent generated data: {simulation_data_path}")

        # 4. RenderAgent: Render VFX video
        print("Orchestrator: Running RenderAgent...")
        render_output_dir = os.path.join(output_base_dir, "temp_frames")
        vfx_video_path = self.render_agent.render_vfx(simulation_data_path, render_output_dir, "vfx_output.mp4")
        print(f"Orchestrator: RenderAgent generated VFX video: {vfx_video_path}")

        # 5. Synthesize: Combine VFX video, audio, and subtitles
        print("Orchestrator: Synthesizing final short video...")
        final_video_path = os.path.join(output_base_dir, "final_short.mp4")
        
        # Ensure ffmpeg is available
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, text=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Error: ffmpeg not found. Please install ffmpeg to synthesize videos.")
            return ""

        # ffmpeg command to combine video, audio, and subtitles
        # -i: input video
        # -i: input audio
        # -vf: video filters (subtitles for burning in srt)
        # -c:v: video codec (copy to avoid re-encoding if possible)
        # -c:a: audio codec (copy)
        # -y: overwrite output file if it exists
        ffmpeg_cmd = [
            "ffmpeg",
            "-y",  # Overwrite output file without asking
            "-i", vfx_video_path,  # Input video
            "-i", audio_path,      # Input audio
            "-vf", f"subtitles={subtitle_path}", # Burn in subtitles
            "-c:v", "libx264", # Re-encode video to ensure subtitle burning
            "-c:a", "aac", # Re-encode audio to a common format
            "-map", "0:v:0", # Map video stream from first input
            "-map", "1:a:0", # Map audio stream from second input
            final_video_path
        ]

        try:
            print(f"Running ffmpeg command: {' '.join(ffmpeg_cmd)}")
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True)
            print(f"Orchestrator: Final short video synthesized to: {final_video_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error during video synthesis: {e.stderr.decode()}")
            final_video_path = "" # Indicate failure
        except FileNotFoundError:
            print("Error: ffmpeg command not found. Please ensure ffmpeg is installed and in your PATH.")
            final_video_path = "" # Indicate failure
        
        return final_video_path
