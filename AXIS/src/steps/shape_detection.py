# AXIS/src/steps/shape_detection.py

import cv2
import numpy as np
from typing import List

from ..pipeline import ProcessingStep, FrameContextBuilder
from ..data_models import Circle, Triangle, Point2D

class CircleDetectionStep(ProcessingStep):
    """A pipeline step to detect circles in a frame."""
    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        context = builder.build()
        frame = context.original_frame

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred_frame = cv2.medianBlur(gray_frame, 5)

        circles = cv2.HoughCircles(
            blurred_frame,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=50,      # Minimum distance between detected centers
            param1=100,      # Upper threshold for the internal Canny edge detector
            param2=30,       # Threshold for center detection
            minRadius=10,    # Minimum radius
            maxRadius=100    # Maximum radius
        )

        detected_circles: List[Circle] = []
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                # Convert numpy types to standard Python types for JSON serialization
                center = Point2D(x=int(i[0]), y=int(i[1]))
                radius = int(i[2])
                detected_circles.append(Circle(center=center, radius=radius))
        
        print(f"Detected {len(detected_circles)} circles.")
        builder.set_circles(detected_circles)
        return builder

class TriangleDetectionStep(ProcessingStep):
    """A pipeline step to detect triangles in a frame."""
    def execute(self, builder: FrameContextBuilder) -> FrameContextBuilder:
        context = builder.build()
        frame = context.original_frame

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                                     cv2.THRESH_BINARY_INV, 11, 2)

        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        detected_triangles: List[Triangle] = []
        for contour in contours:
            if cv2.contourArea(contour) < 100:
                continue

            epsilon = 0.04 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            if len(approx) == 3:
                # Convert numpy types to standard Python types for JSON serialization
                vertices = tuple(Point2D(x=int(pt[0][0]), y=int(pt[0][1])) for pt in approx)
                detected_triangles.append(Triangle(vertices=vertices))

        print(f"Detected {len(detected_triangles)} triangles.")
        builder.set_triangles(detected_triangles)
        return builder