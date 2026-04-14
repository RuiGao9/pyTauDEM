# 1. 从内部模块导入核心类
from .core import pyTauDEM

# 2. 定义版本号（方便用户查看）
__version__ = "0.1.0"

# 3. 定义快捷导出
# 这能确保用户使用 "from pyTauDEM import *" 时只导出你想给他们的类
__all__ = ["pyTauDEM"]

def get_point_terrain(folder, filename, lon, lat, res):
    """
    一个快捷函数：打开文件 -> 获取数据 -> 关闭文件
    """
    from .core import pyTauDEM
    ptd = pyTauDEM(folder, filename)
    try:
        return ptd.get_terrain_data(lon, lat, res)
    finally:
        ptd.close()