export interface Point {
  x: number;
  y: number;
}

export type LinePoint = [number, number];

export interface EasingCurve {
  p1: Point;
  p2: Point;
}

export interface Keyframe {
  frame: number;
  value: number;
}

export interface MotionProperty {
  keyframes: [Keyframe, Keyframe];
  curve: EasingCurve;
}

export interface Motion {
  name: string;
  startFrame: number;
  endFrame: number;
  properties: {
    positionX?: MotionProperty;
    positionY?: MotionProperty;
    rotation?: MotionProperty;
    scale?: MotionProperty;
  };
}

export interface SceneObject {
  id: string;
  type: 'character' | 'object' | 'line' | 'curve'; // Updated types
  color: string;
  startPosition: Point;
  motions: Motion[];
}

export interface Scene {
  id: string;
  duration: number; // in frames
  objects: SceneObject[];
}

// Represents the unique path to a specific curve in the editor
export interface SelectedPropertyPath {
  objectId: string;
  motionName: string;
  propertyName: keyof Motion['properties'];
}