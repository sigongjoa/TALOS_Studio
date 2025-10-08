import React from 'react';
import type { Scene, EasingCurve, SelectedPropertyPath, MotionProperty } from '../types';

interface CurvePresetsProps {
  scene: Scene;
  selectedProperty: SelectedPropertyPath | null;
  onCurveUpdate: (path: SelectedPropertyPath, curve: EasingCurve) => void;
}

const PRESETS: { [key: string]: { cx1: number, cy1: number, cx2: number, cy2: number } } = {
  'Ease In-Out':    { cx1: 0.42, cy1: 0, cx2: 0.58, cy2: 1 },
  'Ease In':        { cx1: 0.42, cy1: 0, cx2: 1, cy2: 1 },
  'Ease Out':       { cx1: 0, cy1: 0, cx2: 0.58, cy2: 1 },
  'Overshoot':      { cx1: 0.34, cy1: 1.56, cx2: 0.64, cy2: 1 },
  'Anticipation':   { cx1: 0.6, cy1: -0.28, cx2: 0.74, cy2: 0.05 },
  'Bouncy':         { cx1: 0.68, cy1: -0.55, cx2: 0.27, cy2: 1.55 },
};

const CurvePresets: React.FC<CurvePresetsProps> = ({ scene, selectedProperty, onCurveUpdate }) => {
  const applyPreset = (preset: { cx1: number; cy1: number; cx2: number; cy2: number; } | 'linear') => {
    if (!selectedProperty) return;
    
    const selectedObject = scene.objects.find(o => o.id === selectedProperty.objectId);
    const selectedMotion = selectedObject?.motions.find(m => m.name === selectedProperty.motionName);
    const motionProperty = selectedMotion?.properties[selectedProperty.propertyName];
    if (!motionProperty || !selectedMotion) return;

    const { keyframes } = motionProperty;
    const p0 = { x: selectedMotion.startFrame, y: keyframes[0].value };
    const p3 = { x: selectedMotion.endFrame, y: keyframes[1].value };

    let newCurve: EasingCurve;

    if (preset === 'linear') {
        newCurve = {
            p1: { x: p0.x + (p3.x - p0.x) / 3, y: p0.y + (p3.y - p0.y) / 3 },
            p2: { x: p0.x + (p3.x - p0.x) * 2 / 3, y: p0.y + (p3.y - p0.y) * 2 / 3 }
        };
    } else {
        newCurve = {
            p1: {
                x: p0.x + (p3.x - p0.x) * preset.cx1,
                y: p0.y + (p3.y - p0.y) * preset.cy1,
            },
            p2: {
                x: p0.x + (p3.x - p0.x) * preset.cx2,
                y: p0.y + (p3.y - p0.y) * preset.cy2,
            },
        };
    }
    
    onCurveUpdate(selectedProperty, newCurve);
  };
  
  if (!selectedProperty) {
    return <div className="flex items-center justify-center h-full text-gray-500 p-4">Select a motion to apply a preset.</div>;
  }

  const { objectId, motionName, propertyName } = selectedProperty;
  const buttonClass = "px-3 py-2 text-xs font-semibold text-gray-200 bg-gray-700/80 rounded-lg hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-emerald-500 transition-all transform hover:scale-105";
  
  return (
    <div className="p-4">
      <h3 className="text-sm font-bold text-gray-400 mb-4">
        Curve Presets for <span className="text-emerald-400 font-mono">[{objectId} &gt; {motionName} &gt; {propertyName}]</span>
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        <button onClick={() => applyPreset('linear')} className={buttonClass}>
          Linear
        </button>
        {Object.entries(PRESETS).map(([name, values]) => (
            <button key={name} onClick={() => applyPreset(values)} className={buttonClass}>
              {name}
            </button>
        ))}
      </div>
    </div>
  );
};

export default CurvePresets;