import React, { useEffect, useRef, useCallback, useState } from 'react';
import type { Scene, EasingCurve, SelectedPropertyPath, Motion, SceneObject, MotionProperty } from '../types';
import CurvePresets from './CurvePresets';
import { AddIcon, TrashIcon } from './icons';

declare const d3: any;

interface TimelineEditorProps {
  scene: Scene;
  selectedProperty: SelectedPropertyPath | null;
  onSelectProperty: (path: SelectedPropertyPath) => void;
  onCurveUpdate: (path: SelectedPropertyPath, curve: EasingCurve) => void;
  onCreateObject: () => void;
  onDeleteObject: (objectId: string) => void;
  currentFrame: number;
}

const DopeSheet = (props: {
  scene: Scene,
  selectedProperty: SelectedPropertyPath | null,
  onSelectProperty: (path: SelectedPropertyPath) => void,
  onCreateObject: () => void,
  onDeleteObject: (objectId: string) => void,
  currentFrame: number
}) => {
  const { scene, selectedProperty, onSelectProperty, onCreateObject, onDeleteObject, currentFrame } = props;
  const totalFrames = scene.duration;

  return (
    <div className="flex-shrink-0 h-1/2 p-2 overflow-y-auto bg-gray-900/50 flex flex-col">
       <div className="flex-shrink-0 flex justify-between items-center mb-2 px-2">
        <h3 className="text-sm font-bold text-gray-400">Dope Sheet / Scene Timeline</h3>
        <button
          onClick={onCreateObject}
          className="flex items-center px-2 py-1 text-xs font-medium text-gray-200 bg-gray-700 rounded-md hover:bg-emerald-600 focus:outline-none"
        >
          <AddIcon className="w-4 h-4 mr-1" />
          Add Object
        </button>
      </div>

      <div className="relative flex-grow">
        <div 
          className="absolute top-0 bottom-0 w-0.5 bg-red-500 z-20"
          style={{ left: `${(currentFrame / totalFrames) * 100}%` }}
        />
        {scene.objects.map(obj => (
          <div key={obj.id} className="mb-2">
            <div className={`group flex items-center h-8 rounded-t bg-gray-700`}>
                <div className="w-40 px-2 text-xs truncate font-mono font-bold">{obj.id}</div>
                <button
                    onClick={(e) => { e.stopPropagation(); onDeleteObject(obj.id); }}
                    className="ml-auto p-1 rounded-full text-gray-500 opacity-0 group-hover:opacity-100 hover:bg-red-500/50 hover:text-red-300 transition-opacity mr-2"
                ><TrashIcon className="w-4 h-4" /></button>
            </div>
            {obj.motions.map(motion => {
                const isSelected = selectedProperty?.objectId === obj.id && selectedProperty?.motionName === motion.name;
                return (
                    <div key={motion.name} 
                        className={`flex items-center h-8 my-px rounded-b transition-colors cursor-pointer ${isSelected ? 'bg-emerald-500/30' : 'bg-gray-800/80 hover:bg-gray-700/80'}`}
                        onClick={() => onSelectProperty({ objectId: obj.id, motionName: motion.name, propertyName: selectedProperty?.propertyName || 'positionY' })}
                    >
                        <div className="w-40 pl-6 pr-2 text-xs truncate font-mono">{motion.name}</div>
                        <div className="w-[calc(100%-10rem)] h-full pr-2">
                        <div className="relative w-full h-full">
                            <div className="absolute h-4 top-1/2 -translate-y-1/2 rounded"
                            style={{ 
                                left: `${(motion.startFrame / totalFrames) * 100}%`,
                                width: `${((motion.endFrame - motion.startFrame) / totalFrames) * 100}%`,
                                backgroundColor: obj.color
                            }} />
                        </div>
                        </div>
                    </div>
                )
            })}
          </div>
        ))}
      </div>
    </div>
  );
};

const GraphEditor = ({ scene, selectedProperty, onCurveUpdate }: { 
    scene: Scene,
    selectedProperty: SelectedPropertyPath | null,
    onCurveUpdate: (path: SelectedPropertyPath, curve: EasingCurve) => void,
}) => {
    const svgRef = useRef<SVGSVGElement>(null);
    
    const selectedObject = scene.objects.find(o => o.id === selectedProperty?.objectId);
    const selectedMotion = selectedObject?.motions.find(m => m.name === selectedProperty?.motionName);
    const motionProperty = selectedMotion?.properties[selectedProperty?.propertyName!];

    const drawChart = useCallback(() => {
        if (!selectedProperty || !motionProperty || !selectedMotion || !selectedObject || !svgRef.current) {
          d3.select(svgRef.current).selectAll("*").remove();
          return;
        }
        
        const { keyframes, curve } = motionProperty;
        const svg = d3.select(svgRef.current);
        svg.selectAll("*").remove();

        const width = svgRef.current.parentElement!.clientWidth;
        const height = svgRef.current.parentElement!.clientHeight;
        const margin = { top: 20, right: 30, bottom: 30, left: 50 };
        const chartWidth = width - margin.left - margin.right;
        const chartHeight = height - margin.top - margin.bottom;
        
        const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);
        
        const yValues = [keyframes[0].value, keyframes[1].value, curve.p1.y, curve.p2.y];
        const yMin = d3.min(yValues);
        const yMax = d3.max(yValues);
        
        const xScale = d3.scaleLinear().domain([selectedMotion.startFrame, selectedMotion.endFrame]).range([0, chartWidth]);
        const yScale = d3.scaleLinear().domain([yMin - 20, yMax + 20]).range([chartHeight, 0]);

        g.append("g").attr("transform", `translate(0,${chartHeight})`).call(d3.axisBottom(xScale)).attr("color", "#6b7280");
        g.append("g").call(d3.axisLeft(yScale)).attr("color", "#6b7280");

        const p0 = { x: keyframes[0].frame, y: keyframes[0].value };
        const p3 = { x: keyframes[1].frame, y: keyframes[1].value };

        const pathData = `M ${xScale(p0.x)},${yScale(p0.y)} C ${xScale(curve.p1.x)},${yScale(curve.p1.y)} ${xScale(curve.p2.x)},${yScale(curve.p2.y)} ${xScale(p3.x)},${yScale(p3.y)}`;
        g.append("path").attr("d", pathData).attr("fill", "none").attr("stroke", selectedObject.color).attr("stroke-width", 2);

        g.append("line").attr("x1", xScale(p0.x)).attr("y1", yScale(p0.y)).attr("x2", xScale(curve.p1.x)).attr("y2", yScale(curve.p1.y)).attr("stroke", "#9ca3af").attr("stroke-width", 1).attr("stroke-dasharray", "4");
        g.append("line").attr("x1", xScale(p3.x)).attr("y1", yScale(p3.y)).attr("x2", xScale(curve.p2.x)).attr("y2", yScale(curve.p2.y)).attr("stroke", "#9ca3af").attr("stroke-width", 1).attr("stroke-dasharray", "4");

        const handles = [{ id: 'p1', point: curve.p1 }, { id: 'p2', point: curve.p2 }];
        const drag = d3.drag().on("drag", (event: any, d: any) => {
            const newX = Math.max(p0.x, Math.min(p3.x, xScale.invert(event.x)));
            const newY = yScale.invert(event.y);
            const newCurve = { ...curve, [d.id]: { x: newX, y: newY } };
            onCurveUpdate(selectedProperty, newCurve);
        });

        g.selectAll(".handle").data(handles).enter().append("circle")
            .attr("class", "handle").attr("r", 6).attr("cx", d => xScale(d.point.x)).attr("cy", d => yScale(d.point.y))
            .attr("fill", selectedObject.color).attr("stroke", "#f0f0f0").attr("stroke-width", 2).style("cursor", "move").call(drag);
        
        [p0, p3].forEach(p => { g.append("rect").attr("x", xScale(p.x) - 5).attr("y", yScale(p.y) - 5).attr("width", 10).attr("height", 10).attr("fill", "#f0f0f0"); });

    }, [selectedProperty, motionProperty, onCurveUpdate, selectedMotion, selectedObject]);

    useEffect(() => {
        const observer = new ResizeObserver(() => drawChart());
        if (svgRef.current?.parentElement) observer.observe(svgRef.current.parentElement);
        drawChart();
        return () => observer.disconnect();
    }, [drawChart]);

    const PropertySelector = () => {
      if(!selectedMotion) return null;
      return (
        <div className="absolute top-2 right-2 flex gap-1">
          {Object.keys(selectedMotion.properties).map(propName => (
            <button key={propName} 
              onClick={() => onCurveUpdate({ ...selectedProperty!, propertyName: propName as keyof Motion['properties'] }, selectedMotion.properties[propName as keyof Motion['properties']]!.curve)}
              className={`px-2 py-1 text-xs rounded ${selectedProperty?.propertyName === propName ? 'bg-emerald-500 text-white' : 'bg-gray-600 text-gray-300 hover:bg-gray-500'}`}
            >
              {propName}
            </button>
          ))}
        </div>
      )
    };

    return (
        <div className="flex-grow p-2 overflow-hidden flex flex-col">
            <h3 className="text-sm font-bold text-gray-400 mb-2">Graph Editor {selectedProperty && `- [${selectedProperty.objectId} > ${selectedProperty.motionName}]`}</h3>
            <div className="flex-grow w-full h-full relative">
                {motionProperty ? (
                    <>
                      <svg ref={svgRef} width="100%" height="100%"></svg>
                      <PropertySelector />
                    </>
                ) : (
                    <div className="flex items-center justify-center h-full text-gray-500">Select a motion to edit its timing curves.</div>
                )}
            </div>
        </div>
    );
};


const TimelineEditor: React.FC<TimelineEditorProps> = (props) => {
  const [activeTab, setActiveTab] = useState<'graph' | 'presets'>('graph');

  return (
    <div className="flex flex-col h-full bg-gray-800">
      <DopeSheet {...props} />
      <div className="w-full h-1 bg-gray-700/50"></div>
      
      <div className="flex-grow flex flex-col overflow-hidden">
        <div className="flex-shrink-0 flex border-b border-gray-700 px-2">
          <button onClick={() => setActiveTab('graph')} className={`px-3 py-2 text-sm font-medium ${activeTab === 'graph' ? 'text-emerald-400 border-b-2 border-emerald-400' : 'text-gray-400'}`}>Graph Editor</button>
          <button onClick={() => setActiveTab('presets')} className={`px-3 py-2 text-sm font-medium ${activeTab === 'presets' ? 'text-emerald-400 border-b-2 border-emerald-400' : 'text-gray-400'}`}>Curve Presets</button>
        </div>

        <div className="flex-grow overflow-auto">
          {activeTab === 'graph' && (
            <GraphEditor 
              scene={props.scene}
              selectedProperty={props.selectedProperty}
              onCurveUpdate={props.onCurveUpdate}
            />
          )}
          {activeTab === 'presets' && (
            <CurvePresets
              scene={props.scene}
              selectedProperty={props.selectedProperty}
              onCurveUpdate={props.onCurveUpdate}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default TimelineEditor;