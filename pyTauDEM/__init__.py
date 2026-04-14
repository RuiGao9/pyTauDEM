from .core import pyTauDEM

# Define the version of the package
__version__ = "0.1.0"

# This ensures that users importing with "from pyTauDEM import *" only get the classes you want to expose
__all__ = ["pyTauDEM"]

def get_point_terrain(folder, filename, lon, lat, res):
    """
    A convenience function: open file -> fetch data -> close file
    """
    
    from .core import pyTauDEM
    ptd = pyTauDEM(folder, filename)
    try:
        return ptd.get_terrain_data(lon, lat, res)
    finally:
        ptd.close()