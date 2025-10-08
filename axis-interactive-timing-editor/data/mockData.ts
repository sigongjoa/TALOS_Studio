import type { Scene } from '../types';

export const MOCK_SCENE: Scene = {
  id: 'S001_Main_Street',
  duration: 120,
  objects: [
    {
      id: 'C001-BouncingBall',
      type: 'character',
      color: '#34d399', // emerald-400
      startPosition: { x: 100, y: 400 },
      motions: [
        {
          name: 'ArcJump',
          startFrame: 0,
          endFrame: 100,
          properties: {
            positionX: {
              keyframes: [{ frame: 0, value: 100 }, { frame: 100, value: 700 }],
              // Linear motion for X-axis
              curve: {
                p1: { x: 33, y: 300 },
                p2: { x: 67, y: 500 },
              },
            },
            positionY: {
              keyframes: [{ frame: 0, value: 400 }, { frame: 100, value: 400 }],
              // Overshoot/Bounce motion for Y-axis
              curve: {
                p1: { x: 30, y: 50 },
                p2: { x: 70, y: 50 },
              },
            },
          },
        },
      ],
    },
    {
      id: 'O002-SlidingBox',
      type: 'object',
      color: '#60a5fa', // blue-400
      startPosition: { x: 800, y: 450 },
      motions: [
        {
          name: 'SlideIn',
          startFrame: 10,
          endFrame: 90,
          properties: {
            positionX: {
              keyframes: [{ frame: 10, value: 800 }, { frame: 90, value: 200 }],
              // Ease-out motion for X-axis
              curve: {
                p1: { x: 10, y: 800 },
                p2: { x: 60, y: 200 },
              },
            },
            positionY: { // Stays constant
              keyframes: [{ frame: 10, value: 450 }, { frame: 90, value: 450 }],
              curve: { p1: { x: 30, y: 450 }, p2: { x: 70, y: 450 } },
            }
          },
        },
      ],
    },
  ],
};