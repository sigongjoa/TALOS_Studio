import React, { useState, useCallback, useEffect } from 'react';
import type { Scene, SceneObject, SelectedPropertyPath } from './types';
import TimelineEditor from './components/TimelineEditor';
import PlaybackControls from './components/PlaybackControls';
import { DownloadIcon } from './components/icons';

const COLOR_PALETTE = ['#fbbf24', '#f87171', '#a78bfa', '#f472b6', '#34d399', '#60a5fa'];
const EMPTY_SCENE: Scene = { id: 'EMPTY', duration: 0, objects: [] };

const transformDataToScene = (data: any[]): Scene => {
  if (!data || data.length === 0) return EMPTY_SCENE;
  
  const objects: SceneObject[] = [];
  const lineMap = new Map<number, SceneObject>();
  const curveMap = new Map<number, SceneObject>();

  data.forEach(frame => {
    if (frame.lines) {
      frame.lines.forEach((line: any) => {
        if (!lineMap.has(line.id)) {
          const newObj: SceneObject = {
            id: `line-${line.id}`,
            type: 'line',
            color: COLOR_PALETTE[objects.length % COLOR_PALETTE.length],
            startPosition: { x: 0, y: 0 },
            motions: [{ name: 'Tracked Line', startFrame: frame.frame_index, endFrame: frame.frame_index, properties: {} }],
          };
          lineMap.set(line.id, newObj);
          objects.push(newObj);
        }
        const existingObj = lineMap.get(line.id)!;
        existingObj.motions[0].endFrame = frame.frame_index;
      });
    }
    if (frame.curves) {
      frame.curves.forEach((curve: any) => {
        if (!curveMap.has(curve.id)) {
          const newObj: SceneObject = {
            id: `curve-${curve.id}`,
            type: 'curve',
            color: COLOR_PALETTE[objects.length % COLOR_PALETTE.length],
            startPosition: { x: 0, y: 0 },
            motions: [{ name: 'Fitted Curve', startFrame: frame.frame_index, endFrame: frame.frame_index, properties: {} }],
          };
          curveMap.set(curve.id, newObj);
          objects.push(newObj);
        }
        const existingObj = curveMap.get(curve.id)!;
        existingObj.motions[0].endFrame = frame.frame_index;
      });
    }
  });

  return {
    id: 'S_Backend_Data',
    duration: data.length > 0 ? data.length - 1 : 0,
    objects: objects,
  };
};

const ImageView: React.FC<{ src: string }> = ({ src }) => (
    <div className="w-full h-full bg-gray-900 flex items-center justify-center border border-gray-700 rounded-lg overflow-hidden">
        <img src={src} className="max-w-full max-h-full object-contain" alt="" />
    </div>
);

function App() {
  const [rawFrames, setRawFrames] = useState<any[]>([]);
  const [scene, setScene] = useState<Scene>(EMPTY_SCENE);
  const [selectedProperty, setSelectedProperty] = useState<SelectedPropertyPath | null>(null);
  const [currentFrame, setCurrentFrame] = useState<number>(0);

  useEffect(() => {
    const streamData = async () => {
      try {
        const response = await fetch('/scene_data.json');
        if (!response.body) {
          console.error("Response body is null");
          return;
        }
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        const BATCH_SIZE = 100;

        const processBatch = (batch: any[]) => {
          if (batch.length > 0) {
            setRawFrames(prevFrames => [...prevFrames, ...batch]);
          }
        };

        let frameBatch: any[] = [];

        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            processBatch(frameBatch);
            break;
          }
          
          buffer += decoder.decode(value, { stream: true });

          let lastPos = 0;
          let braceCount = 0;
          let objectStartIndex = -1;

          for (let i = 0; i < buffer.length; i++) {
            const char = buffer[i];
            if (char === '{') {
              if (braceCount === 0) objectStartIndex = i;
              braceCount++;
            } else if (char === '}') {
              if (braceCount > 0) braceCount--;
              if (braceCount === 0 && objectStartIndex !== -1) {
                const objectStr = buffer.substring(objectStartIndex, i + 1);
                try {
                  const frameData = JSON.parse(objectStr);
                  frameBatch.push(frameData);

                  if (frameBatch.length >= BATCH_SIZE) {
                    processBatch(frameBatch);
                    frameBatch = [];
                    await new Promise(resolve => setTimeout(resolve, 0));
                  }
                } catch (e) {
                  // Incomplete JSON object, wait for more data
                }
                lastPos = i + 1;
                objectStartIndex = -1;
              }
            }
          }

          if (lastPos > 0) {
            buffer = buffer.slice(lastPos);
          }
        }
      } catch (error) {
        console.error("Failed to fetch or process stream:", error);
      }
    };

    streamData();
  }, []);

  useEffect(() => {
    if (rawFrames.length > 0) {
      setScene(transformDataToScene(rawFrames));
    }
  }, [rawFrames]);

  const handleSelectProperty = useCallback((path: SelectedPropertyPath) => setSelectedProperty(path), []);
  const handleExport = useCallback(() => { /* Export logic */ }, [scene]);

  const frameDir = `/output_images/frame_${String(currentFrame).padStart(4, '0')}`;

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-gray-200 font-sans">
      <header className="p-4 border-b border-gray-700 shadow-md bg-gray-800 flex justify-between items-center">
        <div>
            <h1 className="text-xl font-bold text-emerald-400">AXIS Scene Timing Editor</h1>
            <p className="text-sm text-gray-400">Debug View: Lines & Curves</p>
        </div>
        <button onClick={handleExport} className="flex items-center px-4 py-2 text-sm font-medium text-gray-200 bg-gray-700 rounded-md hover:bg-emerald-600">
          <DownloadIcon className="w-4 h-4 mr-2" />
          Export JSON
        </button>
      </header>
      
      <main className="flex-grow flex flex-row p-4 gap-4 overflow-hidden">
        <div className="flex-grow flex flex-col gap-4 overflow-y-auto">
          <div className="grid grid-cols-2 grid-rows-2 gap-4">
            <ImageView src={`${frameDir}/original.png`} />
            <ImageView src={`${frameDir}/lines.png`} />
            <ImageView src={`${frameDir}/curves.png`} />
            <ImageView src={`${frameDir}/overlay.png`} />
          </div>
          <div className="flex-shrink-0">
            <PlaybackControls
              currentFrame={currentFrame}
              totalFrames={scene.duration}
              onFrameChange={setCurrentFrame}
            />
          </div>
        </div>
        <div id="dope-sheet-container" className="flex-shrink-0 w-2/5 max-w-2xl border border-gray-700 rounded-lg bg-gray-800/50 overflow-y-auto">
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