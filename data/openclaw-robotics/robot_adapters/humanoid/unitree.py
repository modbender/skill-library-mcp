"""Unitree Humanoid Robots (G1, H1)"""

import numpy as np
from typing import Optional, List

from ..base import RobotAdapter, RobotState, TaskResult, RobotType


class UnitreeG1Adapter(RobotAdapter):
    """Unitree G1 Humanoid"""
    
    ROBOT_CODE = "unitree_g1"
    ROBOT_NAME = "Unitree G1"
    BRAND = "Unitree"
    ROBOT_TYPE = RobotType.HUMANOID
    
    def connect(self) -> bool:
        self.connected = True
        return True
    
    def disconnect(self) -> None:
        self.connected = False
    
    def get_state(self) -> RobotState:
        return RobotState(battery_level=90.0, temperature=32.0)
    
    def move(self, x: float, y: float, yaw: float) -> TaskResult:
        return TaskResult(True, f"Move: x={x}, y={y}")
    
    def stop(self) -> TaskResult:
        return TaskResult(True, "Stopped")
    
    def stand(self) -> TaskResult:
        return TaskResult(True, "Stand executed")
    
    def sit(self) -> TaskResult:
        return TaskResult(True, "Sit executed")
    
    def go_to(self, position: List[float]) -> TaskResult:
        return TaskResult(True, f"Go to {position}")
    
    def move_arm(self, arm: str, target: List[float]) -> TaskResult:
        return TaskResult(True, f"Move {arm} arm to {target}")
    
    def play_action(self, action_name: str) -> TaskResult:
        return TaskResult(True, f"Play: {action_name}")


class UnitreeH1Adapter(UnitreeG1Adapter):
    ROBOT_CODE = "unitree_h1"
    ROBOT_NAME = "Unitree H1"
