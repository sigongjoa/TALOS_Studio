import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParameters } from '../context/ParameterContext';
import ParameterEditor from '../components/ParameterEditor';

const API_BASE_URL = 'http://localhost:5000/api';

const PreviewPage = () => {
  const { effectDescription, setEffectDescription, simulationParams, setSimulationParams, setVisualizationParams } = useParameters();
  const [logs, setLogs] = useState([]);
  const [previewFrames, setPreviewFrames] = useState([]);
  const [currentFrameIndex, setCurrentFrameIndex] = useState(0);
  const [status, setStatus] = useState('idle');
  const [previewDurationFrames, setPreviewDurationFrames] = useState(30);
  const [isPlaying, setIsPlaying] = useState(false); // New state for playback
  const [playbackSpeed, setPlaybackSpeed] = useState(100); // New state for playback speed (ms per frame)

  const handleInferParams = async () => {
    setLogs(['Inferring parameters from LLM...']);
    setStatus('inferring');
    setPreviewFrames([]);
    setCurrentFrameIndex(0);
    setIsPlaying(false); // Stop playback if running
    try {
      const response = await axios.post(`${API_BASE_URL}/get_llm_inferred_params`, {
        effect_description: effectDescription,
      });
      if (response.data.status === 'success') {
        setSimulationParams(response.data.simulation_params);
        setVisualizationParams(response.data.visualization_params);
        setLogs(prev => [...prev, 'Parameters inferred successfully.']);
        setStatus('idle');
      } else {
        const errorMsg = `Parameter inference failed: ${response.data.message}`;
        setLogs(prev => [...prev, errorMsg]);
        console.error(errorMsg);
        setStatus('failed');
      }
    } catch (error) {
      const errorMsg = `API Error during inference: ${error.response?.data?.message || error.message}`;
      setLogs(prev => [...prev, errorMsg]);
      console.error(errorMsg);
      setStatus('failed');
    }
  };

  const handleRunPreview = async () => {
    setLogs(['Generating preview...']);
    setStatus('previewing');
    setPreviewFrames([]);
    setCurrentFrameIndex(0);
    setIsPlaying(false); // Stop playback if running
    try {
      const response = await axios.post(`${API_BASE_URL}/run_preview`, {
        simulation_params: simulationParams,
        preview_settings: {
          duration_frames: previewDurationFrames,
        },
      });
      if (response.data.status === 'success') {
        setPreviewFrames(response.data.preview_data.frames);
        setLogs(prev => [...prev, 'Preview frames generated successfully.']);
        setStatus('idle');
      } else {
        const errorMsg = `Preview generation failed: ${response.data.message}`;
        setLogs(prev => [...prev, errorMsg]);
        console.error(errorMsg);
        setStatus('failed');
      }
    } catch (error) {
      const errorMsg = `API Error during preview: ${error.response?.data?.message || error.message}`;
      setLogs(prev => [...prev, errorMsg]);
      console.error(errorMsg);
      setStatus('failed');
    }
  };

  const handleSliderChange = (event) => {
    setCurrentFrameIndex(parseInt(event.target.value, 10));
    setIsPlaying(false); // Pause playback on manual slider change
  };

  const togglePlayback = () => {
    setIsPlaying(!isPlaying);
  };

  // Effect hook for automatic playback
  useEffect(() => {
    let intervalId;
    if (isPlaying && previewFrames.length > 0) {
      intervalId = setInterval(() => {
        setCurrentFrameIndex(prevIndex => {
          if (prevIndex === previewFrames.length - 1) {
            return 0; // Loop back to start
          }
          return prevIndex + 1;
        });
      }, playbackSpeed);
    } else if (!isPlaying && intervalId) {
      clearInterval(intervalId);
    }
    return () => clearInterval(intervalId); // Cleanup on unmount or isPlaying/previewFrames change
  }, [isPlaying, previewFrames, playbackSpeed]);

  return (
    <div className="page-content">
      <h2>1. Define & Preview Effect</h2>
      <div className="main-container">
        <div className="controls-panel">
          <h3>Effect Description</h3>
          <p>Describe the visual effect you want to create.</p>
          <div>
            <label>VFX Type:</label>
            <input
              type="text"
              value={effectDescription.vfx_type}
              onChange={(e) => setEffectDescription({ ...effectDescription, vfx_type: e.target.value })}
            />
          </div>
          <div>
            <label>Style:</label>
            <input
              type="text"
              value={effectDescription.style}
              onChange={(e) => setEffectDescription({ ...effectDescription, style: e.target.value })}
            />
          </div>
          <button onClick={handleInferParams} disabled={status === 'inferring' || status === 'previewing'}>
            Infer Parameters from LLM
          </button>

          <h3>Simulation Parameters</h3>
          <p>Adjust the physical properties of the fluid simulation.</p>
          <ParameterEditor params={simulationParams} setParams={setSimulationParams} />

          <div style={{ marginTop: '20px' }}>
            <label htmlFor="previewDurationFrames">Preview Duration (Frames):</label>
            <input
              id="previewDurationFrames"
              type="number"
              value={previewDurationFrames}
              onChange={(e) => setPreviewDurationFrames(parseInt(e.target.value, 10))}
              min="1"
              style={{ marginLeft: '10px', width: '80px' }}
            />
          </div>

          <button onClick={handleRunPreview} disabled={status === 'inferring' || status === 'previewing'}>
            Generate Preview
          </button>
        </div>

        <div className="results-container">
          <div className="status-panel">
            <h3>Logs</h3>
            <div className="log-console" style={{ height: '150px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px', backgroundColor: '#f5f5f5' }}>
              {logs.map((log, index) => (
                <p key={index} style={{ margin: '0', fontFamily: 'monospace', fontSize: '12px' }}>{log}</p>
              ))}
            </div>
          </div>

          <div className="results-panel">
            <h3>Preview</h3>
            {status === 'previewing' && <p>Generating preview frames...</p>}
            {previewFrames.length > 0 ? (
              <>
                <img src={`data:image/png;base64,${previewFrames[currentFrameIndex]}`} alt="Simulation Preview" style={{ maxWidth: '100%', border: '1px solid #ddd' }} />
                <div style={{ marginTop: '10px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <button onClick={togglePlayback} disabled={previewFrames.length === 0}>
                    {isPlaying ? 'Pause' : 'Play'}
                  </button>
                  <input
                    type="range"
                    min="0"
                    max={previewFrames.length - 1}
                    value={currentFrameIndex}
                    onChange={handleSliderChange}
                    style={{ flexGrow: 1 }}
                  />
                  <p>Frame: {currentFrameIndex + 1} / {previewFrames.length}</p>
                  <label htmlFor="playbackSpeed">Speed (ms/frame):</label>
                  <input
                    id="playbackSpeed"
                    type="number"
                    value={playbackSpeed}
                    onChange={(e) => setPlaybackSpeed(Math.max(50, parseInt(e.target.value, 10)))}
                    min="50"
                    max="1000"
                    style={{ width: '60px' }}
                  />
                </div>
              </>
            ) : (
              <p>No preview generated yet. Click "Generate Preview" to see the simulation result.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PreviewPage;
