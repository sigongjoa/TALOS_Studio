import os
import pytest
import subprocess
import json

from src.render_agent.render_agent import RenderAgent

@pytest.fixture
def render_agent():
    return RenderAgent()

def test_render_vfx_properties(render_agent, tmp_path):
    # Create a dummy simulation data file with frames data
    dummy_sim_data_path = tmp_path / "dummy_sim_data.json"
    dummy_sim_data = {
        "simulation_type": "test",
        "formula_used": "test_formula",
        "frames": [
            {"frame_number": 0, "particles": [{"x": 0.1, "y": 0.1}], "metadata": {"time": 0.0}},
            {"frame_number": 1, "particles": [{"x": 0.2, "y": 0.2}], "metadata": {"time": 0.1}},
            {"frame_number": 2, "particles": [{"x": 0.3, "y": 0.3}], "metadata": {"time": 0.2}}
        ]
    }
    with open(dummy_sim_data_path, "w") as f:
        json.dump(dummy_sim_data, f)

    output_dir = tmp_path / "render_output"
    video_filename = "test_output.mp4"
    
    output_video_path = render_agent.render_vfx(str(dummy_sim_data_path), str(output_dir), video_filename)

    assert os.path.exists(output_video_path)
    assert video_filename in output_video_path

    # Use ffprobe to check video properties
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=duration,width,height,codec_name",
            "-of", "json",
            output_video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        video_info = json.loads(result.stdout)
        
        assert "streams" in video_info
        assert len(video_info["streams"]) > 0
        
        video_stream = video_info["streams"][0]
        assert float(video_stream["duration"]) > 0
        assert video_stream["width"] == 800 # Default figsize=(8,6) with dpi=100
        assert video_stream["height"] == 600 # Default figsize=(8,6) with dpi=100
        assert video_stream["codec_name"] == "h264" # libx264 codec

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        pytest.fail(f"ffprobe failed or ffmpeg not found: {e}")
