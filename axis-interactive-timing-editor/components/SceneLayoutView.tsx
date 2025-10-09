import React, { useRef, useEffect } from 'react';
import type { Scene, SceneObject, SelectedPropertyPath } from '../types';

// This function calculates the position of an object based on keyframes and curves.
// It is kept for compatibility with non-line objects.
const getCubicBezierValue = (t: number, p0: number, p1: number, p2: number, p3: number): number => {
  const u = 1 - t;
  const tt = t * t;
  const uu = u * u;
  const uuu = uu * u;
  const ttt = tt * t;
  let value = uuu * p0 + 3 * uu * t * p1 + 3 * u * tt * p2 + ttt * p3;
  return value;
};

const getPropertyValueAtFrame = (frame: number, object: SceneObject, propertyName: string, defaultValue: number): number => {
    for (const motion of object.motions) {
        if (frame >= motion.startFrame && frame <= motion.endFrame) {
            const prop = motion.properties[propertyName as keyof typeof motion.properties];
            if (prop) {
                const { keyframes, curve } = prop;
                const duration = motion.endFrame - motion.startFrame;
                const timeElapsed = frame - motion.startFrame;
                const t = duration > 0 ? timeElapsed / duration : 1;
                return getCubicBezierValue(t, keyframes[0].value, curve.p1.y, curve.p2.y, keyframes[1].value);
            }
        }
    }
    let lastValue = defaultValue;
    for (const motion of object.motions) {
      if(frame > motion.endFrame){
         const prop = motion.properties[propertyName as keyof typeof motion.properties];
         if(prop) lastValue = prop.keyframes[1].value;
      }
    }
    return lastValue;
};


const SceneLayoutView: React.FC<{ scene: Scene; currentFrame: number; selectedProperty: SelectedPropertyPath | null; }> = ({ scene, currentFrame, selectedProperty }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const { width, height } = container.getBoundingClientRect();
    canvas.width = width;
    canvas.height = height;

    ctx.clearRect(0, 0, width, height);

    // Draw all objects in the scene
    scene.objects.forEach(object => {
      // --- CONDITIONAL RENDERING LOGIC ---
      if (object.type === 'line' && object.frameData) {
        // 1. If it's a line, draw the pre-calculated path
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
      } else {
        // 2. Otherwise, use the original logic to draw a circle
        const { startPosition, color, id } = object;
        const x = getPropertyValueAtFrame(currentFrame, object, 'positionX', startPosition.x);
        const y = getPropertyValueAtFrame(currentFrame, object, 'positionY', startPosition.y);
        
        ctx.beginPath();
        ctx.arc(x, y, 15, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.fillStyle = '#ffffff';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(id, x, y + 25);
      }
    });

  }, [scene, currentFrame, selectedProperty]);

  return (
    <div ref={containerRef} className="w-full h-full">
      <canvas ref={canvasRef} />
    </div>
  );
};

export default SceneLayoutView;