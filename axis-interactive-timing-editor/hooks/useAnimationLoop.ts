import React, { useRef, useEffect, useCallback } from 'react';

// FIX: Refactored hook to prevent stale callback closures and ensure stability.
// The original implementation had a bug where the callback could become stale if the parent component re-rendered while the animation was playing.
export const useAnimationLoop = (
    isPlaying: boolean, 
    callback: (time: number) => void
) => {
  // FIX: Explicitly initialize useRef with undefined to fix "Expected 1 arguments, but got 0" error.
  const requestRef = useRef<number | undefined>(undefined);
  // FIX: Explicitly initialize useRef with undefined to fix "Expected 1 arguments, but got 0" error.
  const previousTimeRef = useRef<number | undefined>(undefined);
  const savedCallback = useRef(callback);

  // Keep savedCallback.current up to date with the latest callback function
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  const animate = useCallback((time: number) => {
    if (previousTimeRef.current !== undefined) {
      const deltaTime = time - previousTimeRef.current;
      savedCallback.current(deltaTime);
    }
    previousTimeRef.current = time;
    requestRef.current = requestAnimationFrame(animate);
  }, []); // `animate` is stable and won't change across renders

  useEffect(() => {
    if (isPlaying) {
      // Reset previousTimeRef on play to avoid a large deltaTime on the first frame
      previousTimeRef.current = undefined;
      requestRef.current = requestAnimationFrame(animate);
    } else {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
        requestRef.current = undefined;
      }
    }
    return () => {
      if(requestRef.current) {
        cancelAnimationFrame(requestRef.current);
        requestRef.current = undefined;
      }
    };
  }, [isPlaying, animate]);
};
