import rasterio
import os
import pandas as pd
from .algorithm import calculate_tarboton_slope

class pyTauDEM:
    def __init__(self, folder_path, filename):
        self.dem_path = os.path.join(folder_path, filename)
        if not os.path.exists(self.dem_path):
            raise FileNotFoundError(f"DEM not found at {self.dem_path}")

    def get_terrain_data(self, lon, lat, resolution):
        with rasterio.open(self.dem_path) as src:
            # 1. 构建 9 个点的相对地理坐标 (X, Y)
            # 注意：在地图坐标系中，North 是 Y 增加，East 是 X 增加
            # 顺序要求: E, SE, S, SW, W, NW, N, NE
            offsets = [
                (resolution, 0),          # East
                (resolution, -resolution), # South-East
                (0, -resolution),         # South
                (-resolution, -resolution),# South-West
                (-resolution, 0),         # West
                (-resolution, resolution), # North-West
                (0, resolution),          # North
                (resolution, resolution)   # North-East
            ]
            
            # 2. 转换中心点坐标
            # 如果 DEM 不是 4326，这里需要 pyproj 转换，暂假设已对齐
            center_x, center_y = lon, lat 
            
            # 3. 采样中心点高度
            e0 = list(src.sample([(center_x, center_y)]))[0][0]
            
            # 4. 采样 8 个邻居高度
            adj_elevations = []
            for dx, dy in offsets:
                px, py = center_x + dx, center_y + dy
                elev = list(src.sample([(px, py)]))[0][0]
                adj_elevations.append(elev)
            
            # 5. 计算坡度
            slope = calculate_tarboton_slope(e0, adj_elevations, resolution)
            
            return {
                "elevation": float(e0),
                "adjacent_elevations": [float(e) for e in adj_elevations],
                "slope": slope
            }