"""Sensor Adapter Base Class"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import time


@dataclass
class SensorData:
    """Sensor data"""
    timestamp: float = field(default_factory=time.time)
    data: any = None


class SensorAdapter(ABC):
    """Base class for sensors"""
    
    SENSOR_CODE: str = ""
    SENSOR_NAME: str = ""
    
    def __init__(self, **kwargs):
        self.connected = False
        
    @abstractmethod
    def connect(self) -> bool:
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        pass
    
    @abstractmethod
    def get_data(self) -> dict:
        pass
