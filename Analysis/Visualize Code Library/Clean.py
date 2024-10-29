import numpy as np
import pandas as pd
import pyproj
import os
import shutil
import re

import geopandas as gpd
import matplotlib.pyplot as plt
from datetime import datetime
from shapely.geometry import Point

from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import Normalize
from matplotlib.colorbar import ColorbarBase
#%%


#%%

current_directory = os.getcwd()

for item in os.listdir(current_directory):
    item_path = os.path.join(current_directory, item)
    

    if os.path.isdir(item_path) and "街道图中转" in item:

        for root, dirs, files in os.walk(item_path, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                os.rmdir(dir_path)
        

        os.rmdir(item_path)

print("已结束所有过程，并清理，源CSV文件已移动到目标文件夹")
