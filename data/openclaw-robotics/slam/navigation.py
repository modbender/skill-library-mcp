"""Navigation Module"""

class Navigator:
    """Navigation using SLAM map"""
    
    def __init__(self, robot, slam):
        self.robot = robot
        self.slam = slam
        
    def navigate(self, goal: Tuple[float, float, float], avoidance: bool = True) -> dict:
        return {"success": True, "path": [goal], "goal": goal}
    
    def set_goal(self, position: List[float]):
        pass
    
    def cancel(self):
        pass
