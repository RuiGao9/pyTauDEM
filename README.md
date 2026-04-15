[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19583013.svg)](https://doi.org/10.5281/zenodo.19583013)
![Visitors Badge](https://visitor-badge.laobi.icu/badge?page_id=RuiGao9/pyTauDEM)<br>

# Topographic feature extraction via Python-based TauDEM algorithm
This repository used the TauDEM algorithm introduced by [Tarbuton (1997)](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/96wr03137) for slope calculation and a few other topographic feature extraction based on DEM data.

## How to use this repository
### Repository installation
```bash
pip install "git+https://github.com/RuiGao9/pyTauDEM.git"
```

### Required inputs
- `demo_folder`: the folder contains the target DEM data;
- `filename`: the DEM file name (TIFF format);
- `res`: the pixel resolution of the DEM;
- `latitude` and `longitude`: the latitude and longitude of the target point (pixel).

### How to get the topographic feature? 
`run_pyTauDEM.ipynb` is the demo notebook for the topographic feature extraction. You can also check the demo code below to run the program.

```python
import pyTauDEM

# Define paths and parameters
dem_folder = r"D:\1_Postdoc\0_Data\DEM_Tiff"
filename = "ca_srtm_30m.tif"
res = 30
target_lon, target_lat = -120.112906, 36.336222

# Call function for the target point
ptd = pyTauDEM.pyTauDEM(dem_folder, filename)
results = ptd.get_terrain_data(target_lon, target_lat, res, verbose=True)
# Plot the location of the target point on the map (optional)
ptd.plot_location(target_lon, target_lat, buffer=6, verbose=True)
ptd.close()

# Extracting values from the results dictionary
elev, std, diff, slope = results['elevation'], results['std_elevation'], results['max_elevation_difference'], results['slope']
# Elevation for those adjacent 8 grids
[e, se, s, sw, w, nw, n, ne] = results['adjacent_elevations']

# Print the results
print(f"Target point elevation: {results['elevation']:.2f} m")
print(f"Elevation standard deviation (STD): {results['std_elevation']:.2f} m")
print(f"Local maximum elevation difference (Range): {results['max_elevation_difference']:.2f} m")
print(f"TauDEM slope: {results['slope']:.2f}")
print(results['adjacent_elevations'])
```

### Functions and outputs in this repository
- `get_terrain_data()`: the results will be saved as a dictionary under:
  -  `elevation`: the elevation of the target point/pixel;
  -  `std_elevation`: the standard deviation of those grids (totally 9 grids);
  -  `max_elevation_difference`: the maximum difference between elevations;
  -  `slope`: the TauDEM slope;
  -  `adjacent_elevations`: the elevation for those 8 adjacent grid start clockwise from the east grid.
- `plot_location()`: providing a brief idea about where the target location is (within USA only now). 

## How to cite this work
Gao, R., Khan, M., & Viers, J. H. (2026). Topographic feature extraction via Python-based TauDEM algorithm (v0.1.0). Zenodo. https://doi.org/10.5281/zenodo.19583013

## Reference
Tarboton, D. G. (1997). A new method for the determination of flow directions and upslope areas in grid digital elevation models. Water resources research, 33(2), 309-319.

## Repository update information
- Creation date: 2026-04-14
- Last update: 2026-04-14
- Contact: If you encounter any issues or have questions, please contact Rui Gao at Rui.Ray.Gao@gmail.com