"""Robot Factory"""

from typing import Optional, Dict, Type
from .base import RobotAdapter


class RobotFactory:
    """Factory for creating robot adapters"""
    
    _registry: Dict[str, Type[RobotAdapter]] = {}
    
    @classmethod
    def register(cls, robot_code: str):
        def decorator(adapter_class: Type[RobotAdapter]):
            cls._registry[robot_code] = adapter_class
            return adapter_class
        return decorator
    
    @classmethod
    def create(cls, robot_code: str, ip: str = "192.168.12.1", **kwargs) -> Optional[RobotAdapter]:
        if robot_code not in cls._registry:
            raise ValueError(f"Unknown: {robot_code}. Available: {list(cls._registry.keys())}")
        return cls._registry[robot_code](ip=ip, **kwargs)
    
    @classmethod
    def list_supported(cls) -> list:
        return list(cls._registry.keys())


from .quadruped import UnitreeGO1Adapter, UnitreeGO2Adapter
from .humanoid import UnitreeG1Adapter, UnitreeH1Adapter

RobotFactory.register("unitree_go1")(UnitreeGO1Adapter)
RobotFactory.register("unitree_go2")(UnitreeGO2Adapter)
RobotFactory.register("unitree_g1")(UnitreeG1Adapter)
RobotFactory.register("unitree_h1")(UnitreeH1Adapter)

# Future robots (placeholders)
# RobotFactory.register("wheeled_robot")(WheeledRobotAdapter)
# RobotFactory.register("drone")(DroneAdapter)
# RobotFactory.register("bipedal")(BipedalRobotAdapter)
