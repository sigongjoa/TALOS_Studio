import React, { useState, useCallback, useEffect, useRef } from 'react';
import type { Scene, SceneObject, SelectedPropertyPath } from './types';
import VideoView from './components/VideoView';
import LineCanvas from './components/LineCanvas';
import TimelineEditor from './components/TimelineEditor';
import PlaybackControls from './components/PlaybackControls';
import { DownloadIcon } from './components/icons';

const COLOR_PALETTE = [
  '#fbbf24', '#f87171', '#a78bfa', '#f472b6', '#34d399', '#60a5fa',
];

const EMPTY_SCENE: Scene = {
  id: 'EMPTY',
  duration: 0,
  objects: [],
};

const transformLineDataToScene = (lineData: any[]): Scene => {
  if (!lineData || lineData.length === 0) return EMPTY_SCENE;
  const linesById = new Map<number, { id: number, frames: { frameIndex: number, points: [number, number][] }[] }>();
  lineData.forEach(frame => {
    if (!frame.lines) return;
    frame.lines.forEach((line: any) => {
      if (!linesById.has(line.id)) {
        linesById.set(line.id, { id: line.id, frames: [] });
      }
      linesById.get(line.id)!.frames.push({ frameIndex: frame.frame_index, points: line.points });
    });
  });

  const sceneObjects: SceneObject[] = Array.from(linesById.values()).map((lineGroup, index) => {
    const startFrame = Math.min(...lineGroup.frames.map(f => f.frameIndex));
    const endFrame = Math.max(...lineGroup.frames.map(f => f.frameIndex));
    const frameDataMap: { [key: number]: [number, number][] } = {};
    lineGroup.frames.forEach(frame => { frameDataMap[frame.frameIndex] = frame.points; });

    return {
      id: `line-${lineGroup.id}`,
      type: 'line',
      color: COLOR_PALETTE[index % COLOR_PALETTE.length],
      startPosition: { x: 0, y: 0 },
      motions: [{ name: 'Tracked Path', startFrame, endFrame, properties: {} }],
      frameData: frameDataMap,
    };
  });

  return {
    id: 'S_Backend_Data',
    duration: lineData.length > 0 ? lineData.length - 1 : 0,
    objects: sceneObjects,
  };
};

const PlaceholderView: React.FC<{ title: string }> = ({ title }) => (
    <div className="w-full h-full bg-gray-800/50 flex items-center justify-center border border-gray-700 rounded-lg">
        <p className="text-gray-500">{title}</p>
    </div>
);

function App() {
  const [scene, setScene] = useState<Scene>(EMPTY_SCENE);
  const [selectedProperty, setSelectedProperty] = useState<SelectedPropertyPath | null>(null);
  const [currentFrame, setCurrentFrame] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [viewAspectRatio, setViewAspectRatio] = useState(16/9);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    fetch('/scene_data.json')
      .then(response => response.json())
      .then(data => setScene(transformLineDataToScene(data)))
      .catch(error => console.error("Failed to fetch or transform scene_data.json:", error));
  }, []);

  // Sync video time with the master currentFrame state
  useEffect(() => {
    if (videoRef.current && Math.abs(videoRef.current.currentTime - (currentFrame / 30)) > 0.1) {
        videoRef.current.currentTime = currentFrame / 30; // Assuming 30fps
    }
  }, [currentFrame]);

  // Sync video play/pause with the master isPlaying state
  useEffect(() => {
    if (videoRef.current) {
        isPlaying ? videoRef.current.play() : videoRef.current.pause();
    }
  }, [isPlaying]);

  const handleVideoReady = (element: HTMLVideoElement, width: number, height: number) => {
      videoRef.current = element;
      if (height > 0) {
          setViewAspectRatio(width / height);
      }
  }

  const handleSelectProperty = useCallback((path: SelectedPropertyPath) => setSelectedProperty(path), []);
  const handleExport = useCallback(() => { /* Export logic */ }, [scene]);

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-gray-200 font-sans">
      <header className="p-4 border-b border-gray-700 shadow-md bg-gray-800 flex justify-between items-center">
        <div>
            <h1 className="text-xl font-bold text-emerald-400">AXIS Scene Timing Editor</h1>
            <p className="text-sm text-gray-400">Multi-View Dashboard</p>
        </div>
        <button onClick={handleExport} className="flex items-center px-4 py-2 text-sm font-medium text-gray-200 bg-gray-700 rounded-md hover:bg-emerald-600">
          <DownloadIcon className="w-4 h-4 mr-2" />
          Export JSON
        </button>
      </header>
      
      <main className="flex-grow flex flex-row p-4 gap-4 overflow-hidden">
        
        <div className="flex-grow flex flex-col gap-4">
          {/* 2x2 Grid for viewers */}
          <div className="grid grid-cols-2 grid-rows-2 gap-4 flex-grow">
            <div style={{ aspectRatio: viewAspectRatio }}><VideoView src="/test_video_boxing.mp4" onVideoReady={handleVideoReady} /></div>
            <div style={{ aspectRatio: viewAspectRatio }}><LineCanvas scene={scene} currentFrame={currentFrame} /></div>
            <div style={{ aspectRatio: viewAspectRatio }}><PlaceholderView title="Triangle View (Future)" /></div>
            <div style={{ aspectRatio: viewAspectRatio }}><PlaceholderView title="Circle View (Future)" /></div>
          </div>
          <div className="flex-shrink-0">
            <PlaybackControls
              currentFrame={currentFrame}
              totalFrames={scene.duration}
              isPlaying={isPlaying}
              onPlayPause={setIsPlaying}
              onFrameChange={setCurrentFrame}
            />
          </div>
        </div>

        <div className="flex-shrink-0 w-2/5 max-w-2xl border border-gray-700 rounded-lg bg-gray-800/50 overflow-y-auto">
          <TimelineEditor
            scene={scene}
            selectedProperty={selectedProperty}
            onSelectProperty={handleSelectProperty}
            onCurveUpdate={() => {}}
            onCreateObject={() => {}}
            onDeleteObject={() => {}}
            currentFrame={currentFrame}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
