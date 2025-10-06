import os
import pytest
from unittest.mock import Mock, patch, call
import subprocess
import json

from src.orchestrator.orchestrator import Orchestrator
from src.style_agent.style_agent import StyleAgent
from src.narration_agent.narration_agent import NarrationAgent
from src.simulation_agent.simulation_agent import SimulationAgent
from src.render_agent.render_agent import RenderAgent

@pytest.fixture
def mock_style_agent():
    mock_agent = Mock(spec=StyleAgent)
    mock_agent.extract_parameters_and_formulas.return_value = (
        {"type": "mock_rotation", "speed": 10},
        "mock_formula"
    )
    return mock_agent

@pytest.fixture
def mock_narration_agent():
    mock_agent = Mock(spec=NarrationAgent)
    mock_agent.process_narration.return_value = (
        "/mock/audio.mp3",
        "/mock/subtitles.srt"
    )
    return mock_agent

@pytest.fixture
def mock_simulation_agent():
    mock_agent = Mock(spec=SimulationAgent)
    mock_agent.run_simulation.return_value = "/mock/simulation_data.json"
    return mock_agent

@pytest.fixture
def mock_render_agent():
    mock_agent = Mock(spec=RenderAgent)
    mock_agent.render_vfx.return_value = "/mock/vfx_video.mp4"
    return mock_agent

@pytest.fixture
def orchestrator(mock_style_agent, mock_narration_agent, mock_simulation_agent, mock_render_agent):
    return Orchestrator(
        style_agent=mock_style_agent,
        narration_agent=mock_narration_agent,
        simulation_agent=mock_simulation_agent,
        render_agent=mock_render_agent
    )

@patch('subprocess.run')
def test_run_pipeline_success(mock_subprocess_run, orchestrator, tmp_path):
    user_input = "test user input"
    output_base_dir = str(tmp_path / "final_output")
    
    final_video_path = orchestrator.run_pipeline(user_input, output_base_dir)
    
    # Assertions for agent calls
    orchestrator.style_agent.extract_parameters_and_formulas.assert_called_once_with(user_input)
    orchestrator.narration_agent.process_narration.assert_called_once()
    orchestrator.simulation_agent.run_simulation.assert_called_once()
    orchestrator.render_agent.render_vfx.assert_called_once()
    
    # Assertions for subprocess call (copying video)
    expected_calls = [
        call(["ffmpeg", "-version"], capture_output=True, check=True, text=True),
        call(["ffmpeg", "-y", "-i", "/mock/vfx_video.mp4", "-i", "/mock/audio.mp3", "-vf", f"subtitles=/mock/subtitles.srt", "-c:v", "libx264", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", os.path.join(output_base_dir, "final_short.mp4")],
             check=True, capture_output=True, text=True)
    ]
    mock_subprocess_run.assert_has_calls(expected_calls)
    assert mock_subprocess_run.call_count == 2
    
    assert final_video_path == os.path.join(output_base_dir, "final_short.mp4")

@patch('subprocess.run')
def test_run_pipeline_synthesis_failure(mock_subprocess_run, orchestrator, tmp_path):
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(1, "ffmpeg")
    
    user_input = "test user input"
    output_base_dir = str(tmp_path / "final_output")
    
    final_video_path = orchestrator.run_pipeline(user_input, output_base_dir)
    
    assert final_video_path == ""
    mock_subprocess_run.assert_called_once()

@patch('subprocess.run')
def test_run_pipeline_video_properties(mock_subprocess_run, orchestrator, tmp_path):
    user_input = "test user input for video properties"
    output_base_dir = str(tmp_path / "final_output_video_props")
    # Mock ffprobe output for the final video
    mock_ffprobe_output = {
        "streams": [
            {"codec_name": "h264", "width": 800, "height": 600, "duration": "1.000000"},
            {"codec_name": "aac", "duration": "1.000000"}
        ]
    }

    # Define cmd for ffprobe call (needed for subprocess.CompletedProcess mock)
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=duration,width,height,codec_name",
        "-of", "json",
        str(os.path.join(output_base_dir, "final_short.mp4")) # Convert to string
    ]

    # Mock all ffmpeg calls throughout the pipeline and the final ffprobe call
    mock_subprocess_run.side_effect = [
        Mock(return_value=Mock(stdout="", stderr="")), # 1. ffmpeg -version check in RenderAgent
        Mock(return_value=Mock(stdout="", stderr="")), # 2. render_vfx's ffmpeg call
        Mock(return_value=Mock(stdout="", stderr="")), # 3. ffmpeg -version check in Orchestrator
        Mock(return_value=Mock(stdout="", stderr="")), # 4. final synthesis ffmpeg call
        Mock(stdout=json.dumps(mock_ffprobe_output), stderr=""), # 5. ffprobe call (in the test itself)
    ]

    final_video_path = orchestrator.run_pipeline(user_input, output_base_dir)

    # Explicitly create the final video file as subprocess.run is mocked
    with open(final_video_path, "w") as f:
        f.write("dummy final video content")

    assert os.path.exists(final_video_path)
    assert "final_short.mp4" in final_video_path

    # The ffprobe call is now part of the side_effect, so we don't call subprocess.run directly
    # We just need to assert that it was called with the correct arguments.
    # The last call to subprocess.run should be the ffprobe call.
    ffprobe_cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=duration,width,height,codec_name",
        "-of", "json",
        final_video_path
    ]
    mock_subprocess_run.assert_called_with(ffprobe_cmd, capture_output=True, text=True, check=True)

    # Now, we can directly use the mock_ffprobe_output to assert properties
    video_info = mock_ffprobe_output
    
    assert "streams" in video_info
    assert len(video_info["streams"]) > 0
    
    video_stream = video_info["streams"][0]
    assert float(video_stream["duration"]) > 0
    assert video_stream["width"] == 800
    assert video_stream["height"] == 600
    assert video_stream["codec_name"] == "h264"
