import React, { useRef, useEffect } from 'react';
import type { Scene, SelectedPropertyPath } from '../types';

// Define the type for the line data we expect from the backend
interface Line {
  id: number;
  points: [number, number][];
}

interface FrameData {
  frame_index: number;
  lines: Line[];
}

interface SceneLayoutViewProps {
  scene: Scene; // Keep for other UI components that might need it
  currentFrame: number;
  selectedProperty: SelectedPropertyPath | null;
  lineData: FrameData[]; // The actual data we will render
}

// A cache for line colors
const colorMap: { [key: number]: string } = {};
const getLineColor = (lineId: number): string => {
    if (colorMap[lineId]) {
        return colorMap[lineId];
    }
    // Simple hash function to generate a color from the ID
    const color = `hsl(${(lineId * 47) % 360}, 100%, 50%)`;
    colorMap[lineId] = color;
    return color;
};

const SceneLayoutView: React.FC<SceneLayoutViewProps> = ({ scene, currentFrame, selectedProperty, lineData }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    console.log("--- RUNNING NEW SceneLayoutView RENDER LOGIC ---"); // <-- DEBUG LOG

    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { width, height } = container.getBoundingClientRect();
    canvas.width = width;
    canvas.height = height;

    ctx.clearRect(0, 0, width, height);

    // --- New Drawing Logic ---
    // Find the data for the current frame in our lineData array
    const frameData = lineData[currentFrame];

    if (frameData && frameData.lines) {
      // Iterate over the lines for the current frame and draw them
      frameData.lines.forEach(line => {
        if (!line.points || line.points.length < 2) {
          return; // Cannot draw a line with less than 2 points
        }

        ctx.strokeStyle = getLineColor(line.id);
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(line.points[0][0], line.points[0][1]);

        for (let i = 1; i < line.points.length; i++) {
          ctx.lineTo(line.points[i][0], line.points[i][1]);
        }
        ctx.stroke();
      });
    }
    // --- End of New Drawing Logic ---

  }, [lineData, currentFrame]); // Depend on lineData and currentFrame

  return (
    <div ref={containerRef} className="w-full h-full">
      <canvas ref={canvasRef} />
    </div>
  );
};

export default SceneLayoutView;
