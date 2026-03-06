"""Robot Adapter Base Class"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List
import numpy as np
import time


@dataclass
class RobotState:
    """Robot state"""
    position: np.ndarray = field(default_factory=lambda: np.zeros(3))
    orientation: np.ndarray = field(default_factory=lambda: np.array([0, 0, 0, 1]))
    battery_level: float = 100.0
    temperature: float = 25.0
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        return {
            "position": self.position.tolist(),
            "battery": f"{self.battery_level}%",
            "temperature": f"{self.temperature}°C"
        }


@dataclass  
class TaskResult:
    """Task execution result"""
    success: bool
    message: str = ""
    data: Optional[dict] = None


class RobotType:
    """Robot type constants"""
    QUADRUPED = "quadruped"
    HUMANOID = "humanoid"
    WHEELED = "wheeled"
    AERIAL = "aerial"
    SURFACE = "surface"


class RobotAdapter(ABC):
    """Abstract base class for robot adapters"""
    
    ROBOT_CODE: str = ""
    ROBOT_NAME: str = ""
    BRAND: str = ""
    ROBOT_TYPE: str = RobotType.QUADRUPED
    
    def __init__(self, ip: str = "192.168.12.1", **kwargs):
        self.ip = ip
        self.connected = False
        self.state = RobotState()
        
    @abstractmethod
    def connect(self) -> bool:
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        pass
    
    @abstractmethod
    def get_state(self) -> RobotState:
        pass
    
    @abstractmethod
    def move(self, x: float, y: float, yaw: float) -> TaskResult:
        """Move: x-forward, y-left, yaw-rotation"""
        pass
    
    @abstractmethod
    def stop(self) -> TaskResult:
        pass
    
    def stand(self) -> TaskResult:
        return TaskResult(False, "Not supported")
    
    def sit(self) -> TaskResult:
        return TaskResult(False, "Not supported")
    
    def go_to(self, position: List[float]) -> TaskResult:
        return TaskResult(False, "Not supported")
    
    def play_action(self, action_name: str) -> TaskResult:
        return TaskResult(False, f"Action {action_name} not defined")
    
    def get_info(self) -> dict:
        return {
            "code": self.ROBOT_CODE,
            "name": self.ROBOT_NAME,
            "brand": self.BRAND,
            "type": self.ROBOT_TYPE,
            "ip": self.ip,
            "connected": self.connected
        }

# Export TaskResult for convenience
TaskResult = TaskResult
