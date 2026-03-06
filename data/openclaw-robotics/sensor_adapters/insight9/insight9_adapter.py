"""
Looper Robotics Insight9 RGB-D Camera Adapter
"""

import numpy as np
import time
from dataclasses import dataclass

from ..base import SensorAdapter, SensorData


@dataclass
class Insight9Config:
    """Insight9 configuration"""
    serial: str = ""
    resolution: str = "1080p"
    depth_range: str = "medium"  # near, medium, far


class Insight9Adapter(SensorAdapter):
    """
    Looper Robotics Insight9 RGB-D Camera
    
    Specifications:
    - RGB: 1080P @ 30fps
    - Depth: 0.1-10m range
    - IR: Built-in IR emitter
    - Interface: USB-C
    """
    
    SENSOR_CODE = "insight9"
    SENSOR_NAME = "Looper Robotics Insight9"
    
    def __init__(self, config: Insight9Config = None, **kwargs):
        super().__init__(**kwargs)
        self.config = config or Insight9Config()
        self.running = False
        
    def connect(self) -> bool:
        self.connected = True
        return True
    
    def disconnect(self) -> None:
        self.connected = False
        self.running = False
    
    def start(self):
        self.running = True
        
    def stop(self):
        self.running = False
    
    def get_data(self) -> dict:
        return {
            "rgb": np.zeros((1080, 1920, 3), dtype=np.uint8),
            "depth": np.zeros((1080, 1920), dtype=np.uint16),
            "timestamp": time.time()
        }
    
    def get_intrinsics(self) -> dict:
        return {"fx": 1050.0, "fy": 1050.0, "cx": 960.0, "cy": 540.0}
