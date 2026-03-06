# 导入核心执行类，方便外部框架直接调用
from .main import SalesOratoryMaster, setup

# 定义包的版本，方便管理
__version__ = "1.0.0"

# 定义哪些对象是可以被外部直接 import 的
__all__ = ["SalesOratoryMaster", "setup"]