"""Visual SLAM Module"""

import numpy as np
from typing import Optional, Tuple, List
from dataclasses import dataclass


@dataclass
class Pose:
    """Camera pose"""
    position: np.ndarray
    orientation: np.ndarray
    
    def to_matrix(self) -> np.ndarray:
        return np.eye(4)


class VisualSLAM:
    """Visual SLAM using Insight9"""
    
    def __init__(self, sensor_adapter=None):
        self.sensor = sensor_adapter
        self.running = False
        self.current_pose = Pose(
            position=np.zeros(3),
            orientation=np.array([0, 0, 0, 1])
        )
        
    def start(self):
        self.running = True
        if self.sensor:
            self.sensor.start()
    
    def stop(self):
        self.running = False
        if self.sensor:
            self.sensor.stop()
    
    def get_pose(self) -> Pose:
        return self.current_pose
    
    def get_map(self):
        return None
    
    def save_map(self, path: str):
        pass
    
    def load_map(self, path: str):
        pass
