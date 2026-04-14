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
        # Build transformer: from longitude/latitude (4326) to DEM's own coordinate system
        self.transformer = Transformer.from_crs("EPSG:4326", self.src.crs, always_xy=True)

    def get_terrain_data(self, lon, lat, resolution):
        # 1. Convert longitude and latitude to the DEM's coordinate system (X, Y)
        target_x, target_y = self.transformer.transform(lon, lat)
        
        # 2. Define offsets for the 8 neighboring points (E, SE, S, SW, W, NW, N, NE)
        offsets = [
            (resolution, 0), (resolution, -resolution), (0, -resolution),
            (-resolution, -resolution), (-resolution, 0), (-resolution, resolution),
            (0, resolution), (resolution, resolution)
        ]
        
        # 3. Extract elevation value for the target point
        # Note: sample returns a generator, so we need to convert it to a list to access the value
        e0 = list(self.src.sample([(target_x, target_y)]))[0][0]
        
        # Dealing with invalid values (NoData is usually 32767 or -9999)
        # Suggest checking the specific DEM's nodata value, or use self.src.nodata
        nodata = self.src.nodata if self.src.nodata is not None else 32767
        
        if e0 == nodata or e0 < -100: 
             return {"elevation": None, "slope": None, "adjacent_elevations": []}
            
        # 4. Extract elevation values for the 8 neighboring points
        adj_elevations = []
        for dx, dy in offsets:
            px, py = target_x + dx, target_y + dy  # 修正点：之前这里写的是 center_x
            # Using self.src, not src
            elev = list(self.src.sample([(px, py)]))[0][0]
            
            # In case the neighbor is a nodata value, the slope calculation will explode, so we provide a default handling
            if elev == nodata:
                elev = e0
                
            adj_elevations.append(elev)
        
        # 5. Calculate slope using Tarboton's method
        slope = calculate_tarboton_slope(e0, adj_elevations, resolution)
        
        return {
            "elevation": float(e0),
            "adjacent_elevations": [float(e) for e in adj_elevations],
            "slope": slope
        }


    def plot_location(self, lon, lat, buffer=2.0, verbose=True):
        # 1. Get low-resolution map directly from public libraries
        # This is a lightweight GeoJSON, usually loads quickly, but we also provide a backup URL in case the primary source is down
        # Loading the world map for plotting
        url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
        backup_url = "https://raw.githubusercontent.com/holtzy/The-Python-Graph-Gallery/master/static/data/world.geojson"
        
        try:
            world = gpd.read_file(url)
            if verbose:
                print("Successfully loaded Natural Earth background map.")
        except Exception as e:
            try:
                world = gpd.read_file(backup_url)
                if verbose:
                    print("Successfully loaded backup background map.")
            except Exception:
                # Raise a clear error, reminding the user to check their network or map source
                raise RuntimeError(
                    "\n" + "!"*50 + "\n"
                    "ERROR: Failed to load background map data!\n"
                    "This is usually caused by network issues or broken URLs.\n"
                    "Please check your internet connection or update the 'url' in plot_location().\n"
                    "You can still run get_terrain_data(), but plotting is disabled.\n"
                    "!"*50
                )
        usa = world[world.CONTINENT == "North America"]

        # 2. Build GeoDataFrame for the station location
        gdf_station = gpd.GeoDataFrame(
            [{"name": "Station"}], 
            geometry=[Point(lon, lat)], 
            crs="EPSG:4326"
        )

        # 3. Plotting
        fig, ax = plt.subplots(figsize=(10, 7))
        world.plot(ax=ax, color='#f0f0f0', edgecolor='#aaaaaa')
        gdf_station.plot(ax=ax, color='red', marker='*', markersize=150, zorder=5)

        # 4. Focus on California/ western United States
        ax.set_xlim([lon - buffer, lon + buffer])
        ax.set_ylim([lat - buffer, lat + buffer])
        
        plt.title(f"Site Location: {lon:.4f}, {lat:.4f}")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.show()


    def get_terrain_data(self, lon, lat, resolution_meters, verbose=True):
        if verbose:
            # Diagnostic information for debugging
            print("-" * 30)
            print(f"[pyTauDEM Diagnostic Info]")
            print(f"1. Coordinate Reference System of DEM (CRS): {self.src.crs}")
            
        # 1. I assumed DEM in WGS84 system，the unit is degree
        # Convert resolution from meters to degrees (approximation, valid near the equator)    
        res_degrees = resolution_meters / 111320.0
        
        # Checking the boundary
        bounds = self.src.bounds

        # 2. Latitude and longitude will be directly used for offset, coordinate system is WGS84
        target_x, target_y = lon, lat 
        
        # 3. Define offsets (now in degrees)
        offsets = [
            (res_degrees, 0), (res_degrees, -res_degrees), (0, -res_degrees),
            (-res_degrees, -res_degrees), (-res_degrees, 0), (-res_degrees, res_degrees),
            (0, res_degrees), (res_degrees, res_degrees)
        ]
        
        # 4. The target sampling point
        e0 = list(self.src.sample([(target_x, target_y)]))[0][0]
        
        # 5. Sample the 8 neighboring points
        adj_elevations = []
        for dx, dy in offsets:
            px, py = target_x + dx, target_y + dy
            # Extracting elevation value for the neighboring point
            sample_val = list(self.src.sample([(px, py)]))[0][0]
            adj_elevations.append(float(sample_val))
            
        # 6. Calculate slope (Note: The denominator in the slope calculation formula must be in "meters")
        slope = calculate_tarboton_slope(e0, adj_elevations, resolution_meters)

        # 7. Standard deviation for those 9 grids and the maximum elevation difference
        all_elevations = [e0] + adj_elevations
        std_elev = np.std(all_elevations)
        max_diff = np.ptp(all_elevations)

        if verbose:
            print(f"2. Offset conversion: {resolution_meters} meters ≈ {res_degrees:.6f} degrees")
            print(f"3. DEM coverage area (background map): Lon({bounds.left:.2f} to {bounds.right:.2f}), Lat({bounds.bottom:.2f} to {bounds.top:.2f})")
            print(f"-" * 30)


        return {
            "elevation": float(e0),
            "adjacent_elevations": adj_elevations,
            "slope": slope,
            "std_elevation": std_elev,
            "max_elevation_difference": max_diff
        }
    

    def close(self):
        """Remember to close the raster file when done to free up resources"""
        self.src.close()




