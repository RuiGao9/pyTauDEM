import rasterio
import os
import pandas as pd
from .algorithm import calculate_tarboton_slope
from pyproj import Transformer
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import numpy as np


class pyTauDEM:
    def __init__(self, folder_path, filename):
        self.dem_path = os.path.join(folder_path, filename)
        self.src = rasterio.open(self.dem_path)
        # 建立转换器：从经纬度 (4326) 转换到 DEM 自身的坐标系
        self.transformer = Transformer.from_crs("EPSG:4326", self.src.crs, always_xy=True)

    def get_terrain_data(self, lon, lat, resolution):
        # 1. 把经纬度转成 DEM 对应的地图单位 (X, Y)
        target_x, target_y = self.transformer.transform(lon, lat)
        
        # 2. 定义偏移量
        offsets = [
            (resolution, 0), (resolution, -resolution), (0, -resolution),
            (-resolution, -resolution), (-resolution, 0), (-resolution, resolution),
            (0, resolution), (resolution, resolution)
        ]
        
        # 3. 采样中心点
        # 注意：sample 返回的是一个 generator，需要转成 list 取值
        e0 = list(self.src.sample([(target_x, target_y)]))[0][0]
        
        # 处理无效值 (NoData 通常是 32767 或 -9999)
        # 建议检查具体 DEM 的 nodata 值，或者使用 self.src.nodata
        nodata = self.src.nodata if self.src.nodata is not None else 32767
        
        if e0 == nodata or e0 < -100: 
             return {"elevation": None, "slope": None, "adjacent_elevations": []}
            
        # 4. 采样 8 个邻居高度
        adj_elevations = []
        for dx, dy in offsets:
            px, py = target_x + dx, target_y + dy  # 修正点：之前这里写的是 center_x
            # 使用 self.src 而不是 src
            elev = list(self.src.sample([(px, py)]))[0][0]
            
            # 如果邻居是无效值，坡度计算会爆炸，建议给个默认处理
            if elev == nodata:
                elev = e0 # 或者返回 None 触发错误处理
                
            adj_elevations.append(elev)
        
        # 5. 计算坡度
        slope = calculate_tarboton_slope(e0, adj_elevations, resolution)
        
        return {
            "elevation": float(e0),
            "adjacent_elevations": [float(e) for e in adj_elevations],
            "slope": slope
        }


    def plot_location(self, lon, lat, buffer=2.0):
        import geopandas as gpd
        import matplotlib.pyplot as plt
        from shapely.geometry import Point

        # 1. 直接从公共库下载低分辨率地图
        # 这是一个轻量级的 GeoJSON，通常加载很快
        url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
        try:
            world = gpd.read_file(url)
        except:
            # 如果上面的链接由于网络原因失效，尝试另一个备份链接
            world = gpd.read_file("https://raw.githubusercontent.com/holtzy/The-Python-Graph-Gallery/master/static/data/world.geojson")

        usa = world[world.CONTINENT == "North America"] # 或者 world[world.NAME == "United States of America"]

        # 2. 创建站点点位
        gdf_station = gpd.GeoDataFrame(
            [{"name": "Station"}], 
            geometry=[Point(lon, lat)], 
            crs="EPSG:4326"
        )

        # 3. 绘图
        fig, ax = plt.subplots(figsize=(10, 7))
        world.plot(ax=ax, color='#f0f0f0', edgecolor='#aaaaaa')
        gdf_station.plot(ax=ax, color='red', marker='*', markersize=150, zorder=5)

        # 4. 聚焦到加州/美国西部
        ax.set_xlim([lon - buffer, lon + buffer])
        ax.set_ylim([lat - buffer, lat + buffer])
        
        plt.title(f"Site Location: {lon:.4f}, {lat:.4f}")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.show()


    def get_terrain_data(self, lon, lat, resolution_meters, verbose=True):
        if verbose:
            # --- 诊断信息展示 ---
            print("-" * 30)
            print(f"[pyTauDEM 诊断信息]")
            print(f"1. DEM 坐标系 (CRS): {self.src.crs}")
            print(f"2. 坐标系单位: {self.src.crs.linear_units}")
        # 1. 因为 DEM 是 WGS84，单位是度
        # 我们需要把输入的“米”转成“度”
        
        res_degrees = resolution_meters / 111320.0
        
        # 边界检查
        bounds = self.src.bounds

        # 2. 直接使用经纬度进行偏移（因为目标坐标系就是 WGS84）
        # 这里不需要 transformer，或者 transformer 只是 4326->4326（原地踏步）
        target_x, target_y = lon, lat 
        
        # 3. 定义偏移量（现在单位是度了）
        offsets = [
            (res_degrees, 0), (res_degrees, -res_degrees), (0, -res_degrees),
            (-res_degrees, -res_degrees), (-res_degrees, 0), (-res_degrees, res_degrees),
            (0, res_degrees), (res_degrees, res_degrees)
        ]
        
        # 4. 采样中心点
        e0 = list(self.src.sample([(target_x, target_y)]))[0][0]
        
        # 5. 采样 8 个邻居
        adj_elevations = []
        for dx, dy in offsets:
            px, py = target_x + dx, target_y + dy
            # 执行采样
            sample_val = list(self.src.sample([(px, py)]))[0][0]
            adj_elevations.append(float(sample_val))
            
        # 6. 计算坡度 (注意：计算坡度公式中的分母必须是“米”)
        slope = calculate_tarboton_slope(e0, adj_elevations, resolution_meters)

        # 7. Standard deviation for those 9 grids and the maximum elevation difference
        all_elevations = [e0] + adj_elevations
        std_elev = np.std(all_elevations)
        max_diff = np.ptp(all_elevations)

        if verbose:
            print(f"3. 偏移量换算: {resolution_meters}米 ≈ {res_degrees:.6f}度")
            print(f"4. DEM 覆盖范围: Lon({bounds.left:.2f} to {bounds.right:.2f}), Lat({bounds.bottom:.2f} to {bounds.top:.2f})")
            print(f"DEM extraction is successful!")
            print(f"Elevation at target point: {e0:.2f} m")
            print(f"-" * 30)


        return {
            "elevation": float(e0),
            "adjacent_elevations": adj_elevations,
            "slope": slope,
            "std_elevation": std_elev,
            "max_elevation_difference": max_diff
        }
    

    def close(self):
        """记得关闭文件流"""
        self.src.close()




