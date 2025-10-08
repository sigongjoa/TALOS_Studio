import React, { useState, useCallback } from 'react';
import type { Scene, EasingCurve, SelectedPropertyPath, SceneObject, Motion } from './types';
import { MOCK_SCENE } from './data/mockData';
import SceneLayoutView from './components/SceneLayoutView';
import TimelineEditor from './components/TimelineEditor';
import PlaybackControls from './components/PlaybackControls';
import { DownloadIcon } from './components/icons';


const COLOR_PALETTE = [
  '#fbbf24', // amber-400
  '#f87171', // red-400
  '#a78bfa', // violet-400
  '#f472b6', // pink-400
  '#34d399', // emerald-400
  '#60a5fa', // blue-400
];

function App() {
  const [scene, setScene] = useState<Scene>(MOCK_SCENE);
  const [selectedProperty, setSelectedProperty] = useState<SelectedPropertyPath | null>({
    objectId: MOCK_SCENE.objects[0].id,
    motionName: MOCK_SCENE.objects[0].motions[0].name,
    propertyName: 'positionY',
  });
  const [currentFrame, setCurrentFrame] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [objectCounter, setObjectCounter] = useState(scene.objects.length + 1);

  const handleCurveUpdate = useCallback((path: SelectedPropertyPath, newCurve: EasingCurve) => {
    setScene(prevScene => {
      const newObjects = prevScene.objects.map(obj => {
        if (obj.id !== path.objectId) return obj;
        const newMotions = obj.motions.map(motion => {
          if (motion.name !== path.motionName) return motion;
          const motionProperty = motion.properties[path.propertyName];
          if (!motionProperty) return motion;
          
          const newProperties = {
            ...motion.properties,
            [path.propertyName]: { ...motionProperty, curve: newCurve },
          };
          return { ...motion, properties: newProperties };
        });
        return { ...obj, motions: newMotions };
      });
      return { ...prevScene, objects: newObjects };
    });
  }, []);

  const handleSelectProperty = useCallback((path: SelectedPropertyPath) => {
    setSelectedProperty(path);
  }, []);
  
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

  const handleCreateObject = useCallback(() => {
    const newObjectId = `NewObj-${String(objectCounter).padStart(3, '0')}`;
    const newStartPosition = { x: 150 + ((scene.objects.length % 5) * 100), y: 250 };
    const newColor = COLOR_PALETTE[scene.objects.length % COLOR_PALETTE.length];
    
    const newObject: SceneObject = {
      id: newObjectId,
      type: 'object',
      color: newColor,
      startPosition: newStartPosition,
      motions: [
        {
          name: 'Default Motion',
          startFrame: 0,
          endFrame: 100,
          properties: {
            positionX: {
              keyframes: [{ frame: 0, value: newStartPosition.x }, { frame: 100, value: newStartPosition.x + 200 }],
              curve: { p1: { x: 33, y: newStartPosition.x }, p2: { x: 67, y: newStartPosition.x + 200 } }
            },
            positionY: {
              keyframes: [{ frame: 0, value: newStartPosition.y }, { frame: 100, value: newStartPosition.y }],
              curve: { p1: { x: 33, y: newStartPosition.y }, p2: { x: 67, y: newStartPosition.y } }
            }
          }
        }
      ]
    };

    setScene(prevScene => ({ ...prevScene, objects: [...prevScene.objects, newObject]}));
    setSelectedProperty({
      objectId: newObjectId,
      motionName: newObject.motions[0].name,
      propertyName: 'positionY',
    });
    setObjectCounter(prev => prev + 1);
  }, [scene.objects, objectCounter]);

  const handleDeleteObject = useCallback((objectIdToDelete: string) => {
    setScene(prevScene => ({
        ...prevScene,
        objects: prevScene.objects.filter(obj => obj.id !== objectIdToDelete)
    }));
    if (selectedProperty?.objectId === objectIdToDelete) {
      setSelectedProperty(null);
    }
  }, [selectedProperty]);

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-gray-200 font-sans">
      <header className="p-4 border-b border-gray-700 shadow-md bg-gray-800 flex justify-between items-center">
        <div>
            <h1 className="text-xl font-bold text-emerald-400">AXIS Scene Timing Editor</h1>
            <p className="text-sm text-gray-400">Orchestrating multi-object performance within a single shot.</p>
        </div>
        <button 
          onClick={handleExport}
          className="flex items-center px-4 py-2 text-sm font-medium text-gray-200 bg-gray-700 rounded-md hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-emerald-500 transition-colors"
        >
          <DownloadIcon className="w-4 h-4 mr-2" />
          Export JSON
        </button>
      </header>
      
      <main className="flex-grow flex flex-col p-4 gap-4 overflow-hidden">
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

        <div className="flex-shrink-0 h-[40%] max-h-[45vh] border border-gray-700 rounded-lg bg-gray-800/50 overflow-hidden">
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