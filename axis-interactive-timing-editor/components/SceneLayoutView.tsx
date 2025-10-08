import React, { useRef, useEffect } from 'react';
import type { Scene, SelectedPropertyPath } from '../types';

interface SceneLayoutViewProps {
  scene: Scene;
  currentFrame: number;
  selectedProperty: SelectedPropertyPath | null;
}

const getCubicBezierValue = (t: number, p0: number, p1: number, p2: number, p3: number): number => {
  const u = 1 - t;
  const tt = t * t;
  const uu = u * u;
  const uuu = uu * u;
  const ttt = tt * t;

  let value = uuu * p0; 
  value += 3 * uu * t * p1;
  value += 3 * u * tt * p2;
  value += ttt * p3; 
  
  return value;
};

const getPropertyValueAtFrame = (frame: number, object: any, propertyName: string, defaultValue: number): number => {
    for (const motion of object.motions) {
        if (frame >= motion.startFrame && frame <= motion.endFrame) {
            const prop = motion.properties[propertyName];
            if (prop) {
                const { keyframes, curve } = prop;
                const duration = motion.endFrame - motion.startFrame;
                const timeElapsed = frame - motion.startFrame;
                const t = duration > 0 ? timeElapsed / duration : 1;
                return getCubicBezierValue(t, keyframes[0].value, curve.p1.y, curve.p2.y, keyframes[1].value);
            }
        }
    }
    // If no motion is active, find the last known value or default
    let lastValue = defaultValue;
    for (const motion of object.motions) {
      if(frame > motion.endFrame){
         const prop = motion.properties[propertyName];
         if(prop) lastValue = prop.keyframes[1].value;
      }
    }
    return lastValue;
};


const SceneLayoutView: React.FC<SceneLayoutViewProps> = ({ scene, currentFrame, selectedProperty }) => {
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
    
    // Draw trajectory for the selected motion
    if (selectedProperty) {
      const selectedObject = scene.objects.find(obj => obj.id === selectedProperty.objectId);
      const selectedMotion = selectedObject?.motions.find(m => m.name === selectedProperty.motionName);

      if (selectedObject && selectedMotion) {
        ctx.beginPath();
        ctx.strokeStyle = `${selectedObject.color}80`; // semi-transparent
        ctx.lineWidth = 2;
        ctx.setLineDash([4, 4]);

        for (let frame = selectedMotion.startFrame; frame <= selectedMotion.endFrame; frame++) {
            const x = getPropertyValueAtFrame(frame, selectedObject, 'positionX', selectedObject.startPosition.x);
            const y = getPropertyValueAtFrame(frame, selectedObject, 'positionY', selectedObject.startPosition.y);
            if (frame === selectedMotion.startFrame) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }


    // Draw each object at its current frame position
    scene.objects.forEach(object => {
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
    });

  }, [scene, currentFrame, selectedProperty]);

  return (
    <div ref={containerRef} className="w-full h-full">
      <canvas ref={canvasRef} />
    </div>
  );
};

export default SceneLayoutView;
