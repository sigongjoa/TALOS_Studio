import React, { useRef, useEffect } from 'react';
import type { Scene } from '../types';

interface LineCanvasProps {
  scene: Scene;
  currentFrame: number;
}

const LineCanvas: React.FC<LineCanvasProps> = ({ scene, currentFrame }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { width, height } = container.getBoundingClientRect();
    // Ensure canvas resolution matches its display size
    if (canvas.width !== width || canvas.height !== height) {
        canvas.width = width;
        canvas.height = height;
    }

    ctx.clearRect(0, 0, width, height);

    // Draw all line objects in the scene
    scene.objects.forEach(object => {
      if (object.type === 'line' && object.frameData) {
        const points = object.frameData[currentFrame];
        if (points && points.length >= 2) {
          ctx.strokeStyle = object.color;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(points[0][0], points[0][1]);
          for (let i = 1; i < points.length; i++) {
            ctx.lineTo(points[i][0], points[i][1]);
          }
          ctx.stroke();
        }
      }
    });

  }, [scene, currentFrame]);

  return (
    <div ref={containerRef} className="w-full h-full bg-gray-900">
      <canvas ref={canvasRef} />
    </div>
  );
};

export default LineCanvas;
