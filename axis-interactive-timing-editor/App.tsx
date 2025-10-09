import React, { useState, useCallback, useEffect } from 'react';
import type { Scene, SceneObject, SelectedPropertyPath } from './types';
import SceneLayoutView from './components/SceneLayoutView';
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

// This function transforms the backend data into the frontend's Scene object model.
const transformLineDataToScene = (lineData: any[]): Scene => {
  if (!lineData || lineData.length === 0) {
    return EMPTY_SCENE;
  }

  const linesById = new Map<number, { id: number, frames: { frameIndex: number, points: [number, number][] }[] }>();

  // 1. Group all line points by their persistent ID
  lineData.forEach(frame => {
    if (!frame.lines) return;
    frame.lines.forEach((line: any) => {
      if (!linesById.has(line.id)) {
        linesById.set(line.id, { id: line.id, frames: [] });
      }
      linesById.get(line.id)!.frames.push({ frameIndex: frame.frame_index, points: line.points });
    });
  });

  // 2. Convert each line into a SceneObject
  const sceneObjects: SceneObject[] = Array.from(linesById.values()).map((lineGroup, index) => {
    const startFrame = Math.min(...lineGroup.frames.map(f => f.frameIndex));
    const endFrame = Math.max(...lineGroup.frames.map(f => f.frameIndex));

    const frameDataMap: { [key: number]: [number, number][] } = {};
    lineGroup.frames.forEach(frame => {
      frameDataMap[frame.frameIndex] = frame.points;
    });

    const sceneObject: SceneObject = {
      id: `line-${lineGroup.id}`,
      type: 'line',
      color: COLOR_PALETTE[index % COLOR_PALETTE.length],
      startPosition: { x: 0, y: 0 }, // Placeholder, not used for line type
      motions: [{
        name: 'Tracked Path',
        startFrame: startFrame,
        endFrame: endFrame,
        properties: {}, // Not used for line type
      }],
      frameData: frameDataMap, // The pre-calculated data
    };
    return sceneObject;
  });

  return {
    id: 'S_Backend_Data',
    duration: lineData.length,
    objects: sceneObjects,
  };
};

function App() {
  const [scene, setScene] = useState<Scene>(EMPTY_SCENE);
  const [selectedProperty, setSelectedProperty] = useState<SelectedPropertyPath | null>(null);
  const [currentFrame, setCurrentFrame] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);

  useEffect(() => {
    fetch('/scene_data.json')
      .then(response => response.json())
      .then(data => {
        const transformedScene = transformLineDataToScene(data);
        setScene(transformedScene);
        if (transformedScene.objects.length > 0) {
            // Auto-select the first object to show something in the graph editor
            setSelectedProperty({
                objectId: transformedScene.objects[0].id,
                motionName: transformedScene.objects[0].motions[0].name,
                propertyName: 'positionX' // Placeholder
            });
        }
      })
      .catch(error => console.error("Failed to fetch or transform scene_data.json:", error));
  }, []);

  // Placeholder handlers - not fully functional with line data but prevent crashes
  const handleSelectProperty = useCallback((path: SelectedPropertyPath) => setSelectedProperty(path), []);
  const handleCurveUpdate = useCallback(() => console.log("Curve updates not applicable for tracked line data."), []);
  const handleCreateObject = useCallback(() => console.log("Object creation not applicable when showing tracked data."), []);
  const handleDeleteObject = useCallback(() => console.log("Object deletion not applicable when showing tracked data."), []);
  const handleExport = useCallback(() => {
    const dataStr = JSON.stringify(scene, null, 2);
    const blob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'axis_scene_profile.json';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }, [scene]);

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-gray-200 font-sans">
      <header className="p-4 border-b border-gray-700 shadow-md bg-gray-800 flex justify-between items-center">
        <div>
            <h1 className="text-xl font-bold text-emerald-400">AXIS Scene Timing Editor</h1>
            <p className="text-sm text-gray-400">Displaying Backend-Generated Line Data</p>
        </div>
        <button 
          onClick={handleExport}
          className="flex items-center px-4 py-2 text-sm font-medium text-gray-200 bg-gray-700 rounded-md hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-emerald-500 transition-colors"
        >
          <DownloadIcon className="w-4 h-4 mr-2" />
          Export JSON
        </button>
      </header>
      
      {/* Main container is now a ROW for a left-right layout */}
      <main className="flex-grow flex flex-row p-4 gap-4 overflow-hidden">
        
        {/* Left Panel (Viewer + Controls) */}
        <div className="flex-grow flex flex-col gap-4">
          <div className="flex-grow border border-gray-700 rounded-lg bg-gray-800/50 relative overflow-hidden">
            <SceneLayoutView
              scene={scene}
              currentFrame={currentFrame}
              selectedProperty={selectedProperty}
            />
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

        {/* Right Panel (Dope Sheet / Timeline) */}
        <div className="flex-shrink-0 w-2/5 max-w-2xl border border-gray-700 rounded-lg bg-gray-800/50 overflow-y-auto">
          <TimelineEditor
            scene={scene}
            selectedProperty={selectedProperty}
            onSelectProperty={handleSelectProperty}
            onCurveUpdate={handleCurveUpdate}
            onCreateObject={handleCreateObject}
            onDeleteObject={handleDeleteObject}
            currentFrame={currentFrame}
          />
        </div>
      </main>
    </div>
  );
}

export default App;