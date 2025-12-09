import React from 'react';
import { ResetIcon, ChevronLeftIcon, ChevronRightIcon } from './icons';

interface PlaybackControlsProps {
  currentFrame: number;
  totalFrames: number;
  onFrameChange: React.Dispatch<React.SetStateAction<number>>;
}

const PlaybackControls: React.FC<PlaybackControlsProps> = ({
  currentFrame,
  totalFrames,
  onFrameChange,
}) => {

  const handleScrubberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFrameChange(parseInt(e.target.value, 10));
  };
  
  const handleReset = () => {
    onFrameChange(0);
  };

  const handlePrevFrame = () => {
    onFrameChange(prev => Math.max(0, prev - 1));
  };

  const handleNextFrame = () => {
    onFrameChange(prev => Math.min(totalFrames, prev + 1));
  };

  return (
    <div className="flex items-center gap-4 p-2 bg-gray-800 rounded-lg border border-gray-700">
      <div className="flex items-center gap-2">
        <button
          onClick={handleReset}
          className="p-2 rounded-full hover:bg-gray-700 transition-colors"
          aria-label="Reset"
        >
          <ResetIcon className="w-5 h-5 text-gray-300" />
        </button>
        <button
          onClick={handlePrevFrame}
          className="p-2 rounded-full hover:bg-gray-700 transition-colors"
          aria-label="Previous Frame"
        >
          <ChevronLeftIcon className="w-5 h-5 text-gray-300" />
        </button>
        <button
          onClick={handleNextFrame}
          className="p-2 rounded-full hover:bg-gray-700 transition-colors"
          aria-label="Next Frame"
        >
          <ChevronRightIcon className="w-5 h-5 text-gray-300" />
        </button>
      </div>
      <div className="w-20 text-center font-mono text-sm">
        {String(Math.round(currentFrame)).padStart(3, '0')} / {totalFrames}
      </div>
      <input
        type="range"
        min="0"
        max={totalFrames}
        value={currentFrame}
        onChange={handleScrubberChange}
        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
        style={{
            background: `linear-gradient(to right, #34d399 ${currentFrame/totalFrames * 100}%, #4b5563 ${currentFrame/totalFrames * 100}%)`
        }}
      />
    </div>
  );
};

export default PlaybackControls;