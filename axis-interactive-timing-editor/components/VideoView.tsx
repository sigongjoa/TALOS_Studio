import React, { useEffect, useRef } from 'react';

interface VideoViewProps {
  src: string;
  onVideoReady: (element: HTMLVideoElement, width: number, height: number) => void;
}

const VideoView: React.FC<VideoViewProps> = ({ src, onVideoReady }) => {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const video = videoRef.current;
    if (video) {
      const handleMetadata = () => {
        onVideoReady(video, video.videoWidth, video.videoHeight);
      };
      if (video.readyState >= 1) {
        handleMetadata();
      } else {
        video.addEventListener('loadedmetadata', handleMetadata);
      }
      return () => video.removeEventListener('loadedmetadata', handleMetadata);
    }
  }, [onVideoReady, src]);

  return (
    <div className="w-full h-full bg-black flex items-center justify-center overflow-hidden">
      <video ref={videoRef} src={src} muted loop playsInline className="max-w-full max-h-full" />
    </div>
  );
};

export default VideoView;
