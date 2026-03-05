"""
Unitree Robot Controller Skill for OpenClaw

Control robots via IM (WeCom, Feishu, DingTalk, WhatsApp)
"""

import re
from typing import Optional, Callable
from .robot_adapters import RobotFactory, RobotAdapter
from .im_adapters import WeComAdapter, FeishuAdapter, DingTalkAdapter, WhatsAppAdapter
from .sensor_adapters import Insight9Adapter
from .slam import VisualSLAM, Navigator


class RoboticsSkill:
    """OpenClaw skill for robot control"""
    
    def __init__(self):
        self.robot: Optional[RobotAdapter] = None
        self.im_adapter = None
        self.slam: Optional[VisualSLAM] = None
        self.navigator: Optional[Navigator] = None
        
    def initialize(self, robot: str = "unitree_go2", im: str = "wecom", 
                   robot_ip: str = "192.168.12.1", config: dict = None) -> dict:
        """Initialize robot and IM connection"""
        # Create robot
        self.robot = RobotFactory.create(robot, robot_ip)
        if not self.robot or not self.robot.connect():
            return {"success": False, "error": "Failed to connect robot"}
        
        # Create IM adapter
        if im == "wecom":
            self.im_adapter = WeComAdapter(config)
        elif im == "feishu":
            self.im_adapter = FeishuAdapter(config)
        elif im == "dingtalk":
            self.im_adapter = DingTalkAdapter(config)
        elif im == "whatsapp":
            self.im_adapter = WhatsAppAdapter(config)
        
        if self.im_adapter:
            self.im_adapter.connect()
        
        return {
            "success": True,
            "robot": self.robot.ROBOT_NAME,
            "im": im,
            "connected": True
        }
    
    def execute(self, command: str) -> dict:
        """Execute natural language command"""
        if not self.robot:
            return {"success": False, "error": "Not initialized"}
        
        parsed = self._parse_command(command)
        if parsed["action"] == "unknown":
            return {"success": False, "error": f"Unknown command: {command}"}
        
        return self._execute_action(parsed["action"], parsed["params"])
    
    def _parse_command(self, command: str) -> dict:
        """Parse command to action"""
        patterns = [
            (r"(forward|向前|前进)\s*(\d+(?:\.\d+)?)?\s*m?", "forward", "distance"),
            (r"(backward|向后|后退)\s*(\d+(?:\.\d+)?)?\s*m?", "backward", "distance"),
            (r"(turn.?left|左转)\s*(\d+)?\s*度?", "turn_left", "angle"),
            (r"(turn.?right|右转)\s*(\d+)?\s*度?", "turn_right", "angle"),
            (r"(stand|站立|站起)", "stand", None),
            (r"(sit|坐下)", "sit", None),
            (r"(stop|停止)", "stop", None),
            (r"(wave|挥手)", "wave", None),
            (r"(handshake|握手)", "handshake", None),
        ]
        
        for pattern, action, param_name in patterns:
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                params = {}
                if param_name and len(match.groups()) > 1 and match.group(2):
                    try:
                        params[param_name] = float(match.group(2))
                    except:
                        params[param_name] = 1.0 if param_name == "distance" else 45
                elif param_name:
                    params[param_name] = 1.0 if param_name == "distance" else 45
                return {"action": action, "params": params}
        
        return {"action": "unknown", "params": {}}
    
    def _execute_action(self, action: str, params: dict) -> dict:
        """Execute action on robot"""
        try:
            from .robot_adapters.base import TaskResult
            
            if action == "forward":
                d = params.get("distance", 1.0)
                result = self.robot.move(d, 0, 0)
                
            elif action == "backward":
                d = params.get("distance", 1.0)
                result = self.robot.move(-d, 0, 0)
                
            elif action == "turn_left":
                a = params.get("angle", 45)
                self.robot.move(0, 0, 0.5)
                import time
                time.sleep(abs(a) / 45)
                result = self.robot.stop()
                
            elif action == "turn_right":
                a = abs(params.get("angle", 45))
                self.robot.move(0, 0, -0.5)
                import time
                time.sleep(a / 45)
                result = self.robot.stop()
                
            elif action == "stand":
                result = self.robot.stand()
                
            elif action == "sit":
                result = self.robot.sit()
                
            elif action == "stop":
                result = self.robot.stop()
                
            elif action == "wave":
                result = self.robot.play_action("wave")
                
            elif action == "handshake":
                result = self.robot.play_action("handshake")
                
            else:
                result = TaskResult(False, f"Not implemented: {action}")
            
            return {"success": result.success, "message": result.message}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def start_slam(self, sensor: str = "insight9") -> dict:
        """Start SLAM with Insight9"""
        sensor_adapter = Insight9Adapter()
        if sensor_adapter.connect():
            self.slam = VisualSLAM(sensor_adapter)
            self.slam.start()
            self.navigator = Navigator(self.robot, self.slam)
            return {"success": True, "message": "SLAM started"}
        return {"success": False, "error": "Sensor failed"}
    
    def navigate(self, goal: Tuple[float, float, float]) -> dict:
        """Navigate to goal"""
        if not self.navigator:
            return {"success": False, "error": "SLAM not started"}
        return self.navigator.navigate(goal)
    
    def get_status(self) -> dict:
        """Get robot status"""
        if not self.robot:
            return {"connected": False}
        
        state = self.robot.get_state()
        result = {
            "robot": self.robot.ROBOT_NAME,
            "connected": self.connected,
            **state.to_dict()
        }
        
        if self.slam:
            pose = self.slam.get_pose()
            result["pose"] = pose.position.tolist()
            
        return result
    
    @property
    def connected(self) -> bool:
        return self.robot.connected if self.robot else False


# Global instance
_skill = RoboticsSkill()

# Convenience functions
initialize = _skill.initialize
execute = _skill.execute
start_slam = _skill.start_slam
navigate = _skill.navigate
get_status = _skill.get_status
list_robots = RobotFactory.list_supported
