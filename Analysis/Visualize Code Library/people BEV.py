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
from matplotlib.patches import Patch

from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import Normalize
from matplotlib.colorbar import ColorbarBase

from Base_Map import base_map_path as other_base_map_path
#该文件请 放到与 街道shp加边框.py 同文件夹中
#该py文件只对people历年文件中的EV PHEV CV列进行筛选出图处理，不会对原csv备份移动
#因此该代码只有出图功能

#请在 街道shp加边框.py 前使用，单独后使用记得清理 原csv文件

#若EV PHEV CV列中其中某列全部为0则会显示ValueError: max() arg is an empty sequence
#如果分块处理你设置了多列，但是发现依旧是只有三列，问题出现的原因是0太多了…
#下面为prin()的展示表明了为何有少于预定值的图例发生
#当然如过图例是0但是显示两种颜色，说明大伙都不到1/km2,即人太少了
#目前0被单独列出设为白色

#数据单位从！！千人转换成了人
"""
percentiles = np.percentile(all_BEVple_BEVmean, np.linspace(0, 100, num_bins + 1))
#print(percentiles)
# 将0添加到percentiles的开始位置
percentiles = np.insert(percentiles, 0, 0)
#print(percentiles)
# 去除重复值
percentiles = np.unique(percentiles)
#print(percentiles)
[  0.   0.   0.  16.  72. 510.]
[  0.   0.   0.   0.  16.  72. 510.]
[  0.  16.  72. 510.]
"""
#%%
current_time = datetime.now()
plt.rcParams['font.sans-serif'] = 'Times New Roman'#字体现在是中易黑体
plt.rcParams['font.weight'] = 'bold'#加粗
plt.rcParams['font.size'] = 60#总局字体大小，后面有单独标题大小
base_map_path = other_base_map_path

#folder_name = "shp_Result_output_time_" + current_time.strftime("%Y-%m-%d-%H-%M-%S")
folder_name = "BEV result"
try:
    os.mkdir(folder_name)
    print(f"已创建文件夹：{folder_name}")
except FileExistsError:
    print(f"{folder_name} 文件夹已存在")
    
if not os.path.exists(os.path.join(folder_name, "Geometrically Spaced")):
    os.makedirs(os.path.join(folder_name, "Geometrically Spaced"))

if not os.path.exists(os.path.join(folder_name, "Equal Value")):
    os.makedirs(os.path.join(folder_name, "Equal Value"))
    
#%%
#！！！


base_map_path = base_map_path
base_map = gpd.read_file(base_map_path)



TitleSize = 130 #改标题大小
people_density = {}

years = list(range(2015, 2060))  


output_folder = os.path.join(os.getcwd(), "people BEV街道图中转")
os.makedirs(output_folder, exist_ok=True)

output_folder1 = os.path.join(os.getcwd(), "csv中转")
os.makedirs(output_folder1, exist_ok=True)

for year in years:
    csv_file_path = f"people{year}year.csv"
    
    if os.path.isfile(csv_file_path): 
        df = pd.read_csv(csv_file_path)
        
        # 导出 BEV 列为 1 的数据
        bev_df = df[df['BEV'] == 1]
        bev_output_path = os.path.join(output_folder1, f"people BEV{year}year.csv")
        bev_df.to_csv(bev_output_path, index=False)
        
#%%
#BEV
base_map_path = base_map_path
base_map = gpd.read_file(base_map_path)


people_density = {}

# years = list(range(2010, 2054))  


output_folder = os.path.join(os.getcwd(), "people BEV街道图中转")
os.makedirs(output_folder, exist_ok=True)


for year in years:
    csv_file_path = f'csv中转/people BEV{year}year.csv'
    #print(csv_file_path)
    if os.path.isfile(csv_file_path): 
        df = pd.read_csv(csv_file_path)
        

        x = df['x-coordinate']
        y = df['y-coordinate']
        

        geometry = [Point(xy) for xy in zip(x, y)]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        

        output_shapefile = os.path.join(output_folder, f"people BEV {year} year.shp")
        
        gdf.to_file(output_shapefile)
        
        print(f"{year}已转换WGS84，保存在 {output_shapefile}。")
    else:
        print()


input_folder = "people BEV街道图中转"  
output_folder = "people BEV街道图中转/第一步图像相交结果"  


os.makedirs(output_folder, exist_ok=True)

base_map_path = base_map_path
base_map = gpd.read_file(base_map_path)


base_map['AREA'] = base_map['AREA'].astype(float)  

for filename in os.listdir(input_folder):
    if filename.endswith(".shp"):  
        input_file_path = os.path.join(input_folder, filename)
        gdf_points = gpd.read_file(input_file_path)
        gdf_points = gdf_points.reset_index(drop=True)
        joined_data = gpd.sjoin(gdf_points, base_map, how="left", op="within")
        

        unmatched_points = joined_data[joined_data['index_right'].isnull()]
        
        if not unmatched_points.empty:
            print(f"文件 {filename} 中有 {len(unmatched_points)} 个点没有面。")
        

        joined_data = joined_data.dropna(subset=['index_right'])

        result = joined_data.groupby('index_right')['people-ID'].count().reset_index()
        result_gdf = gpd.GeoDataFrame(result, geometry=base_map.geometry.loc[result['index_right']].reset_index(drop=True), crs=base_map.crs)
        

        missing_face_ids = set(base_map.index) - set(result_gdf['index_right'])
        missing_faces = gpd.GeoDataFrame({'index_right': list(missing_face_ids), 'people-ID': [0] * len(missing_face_ids)}, geometry=base_map.geometry.loc[list(missing_face_ids)].reset_index(drop=True), crs=base_map.crs)

        result_gdf = pd.concat([result_gdf, missing_faces])
        result_gdf['AREA'] = base_map['AREA'].loc[result_gdf['index_right']].reset_index(drop=True)
        result_gdf['BEVmean'] = result_gdf['people-ID'] / result_gdf['AREA'] *1000
        output_file_path = os.path.join(output_folder, filename)
        result_gdf.to_file(output_file_path)

        print(f"处理完成：{filename}，结果已保存到 {output_file_path}")

print("")



shp_folder = "people BEV街道图中转\第一步图像相交结果"  
gdf_list = []

shp_files = [f for f in os.listdir(shp_folder) if f.endswith('.shp')]

for shp_file in shp_files:
    shp_file_path = os.path.join(shp_folder, shp_file)
    gdf = gpd.read_file(shp_file_path)
    gdf_list.append(gdf)


all_BEVple_BEVmean = []

for gdf in gdf_list:
    BEVmean_column_name = "BEVmean"  
    if BEVmean_column_name in gdf.columns:
        rounded_values = gdf[BEVmean_column_name].apply(lambda x: round(x))
        all_BEVple_BEVmean.extend(rounded_values)

max_BEVple_BEVmean_all_years = max(all_BEVple_BEVmean)
min_BEVple_BEVmean_all_years = min(all_BEVple_BEVmean)
#print(all_BEVple_BEVmean)

num_bins = 5

# 等值划分
num_bins = num_bins
BEVmean_range_all_years = [min_BEVple_BEVmean_all_years + (max_BEVple_BEVmean_all_years - min_BEVple_BEVmean_all_years) * i / num_bins for i in range(num_bins + 1)]  # 不要改变这一行
#BEVmean_range_all_years = [min_BEVple_BEVmean_all_years + (max_BEVple_BEVmean_all_years - min_BEVple_BEVmean_all_years) * i / num_bins for i in range(num_bins + 1)]
gdf['bin_BEV'] = pd.cut(gdf[BEVmean_column_name], bins=BEVmean_range_all_years, labels=range(num_bins), duplicates='drop')
for i, (shp_file, gdf) in enumerate(zip(shp_files, gdf_list)):
    year = re.search(r'\d+', shp_file).group()  # 从文件名中提取数字部分
    title = f"Year:{year}"  # 包含提取年份的标题
    fig, ax = plt.subplots(1, 1, figsize=(40, 40))

    cmap = plt.get_cmap('YlGn', num_bins)  

    gdf.plot(column=BEVmean_column_name, ax=ax, cmap=cmap, legend=False)  
    base_map.plot(ax=ax, color='none', edgecolor='black', linewidth=2)

    # 自定义块状图例
    for j in range(num_bins):
        ax.fill_between([], [], color=cmap(j), label=f'{int(BEVmean_range_all_years[j])}-{int(BEVmean_range_all_years[j+1])}')

    # 创建独立的图例对象并添加到子图中
    legend_elements = [Patch(facecolor=cmap(j), edgecolor='black', label=f'{int(BEVmean_range_all_years[j])}-{int(BEVmean_range_all_years[j+1])}')
                       for j in range(num_bins)]
    ax.legend(handles=legend_elements, title="Population Density Range\nUnit: Person/KM2", loc='upper right', fontsize=25)

    plt.title(title, fontsize=TitleSize, fontname='Times New Roman', fontweight='bold') 
    
    output_file_path = os.path.join(folder_name, 'Equal Value', f"{os.path.splitext(shp_file)[0]}.png")
    plt.savefig(output_file_path, dpi=30, bbox_inches='tight')
    plt.close()
    

# 几何划分
nonzero_values = [value for value in all_BEVple_BEVmean if value != 0]
percentiles_all = np.percentile(nonzero_values, np.linspace(0, 100, num_bins + 1))
percentiles_all = np.insert(percentiles_all, 0, 0)
percentiles_all = np.unique(percentiles_all)
#print("Percentiles all:", percentiles_all)

for i, (shp_file, gdf) in enumerate(zip(shp_files, gdf_list)):
    year = re.search(r'\d+', shp_file).group()  # 从文件名中提取数字部分
    title = f"Year:{year}"  # 包含提取年份的标题，此处改标题
    fig, ax = plt.subplots(1, 1, figsize=(40, 40))

    cmap = plt.get_cmap('YlGn', len(percentiles_all) - 1)

    # 将数据为0的地块单独设置为白色
    gdf_zero = gdf[gdf[BEVmean_column_name] == 0]
    gdf_nonzero = gdf[gdf[BEVmean_column_name] != 0]

    gdf_nonzero['bin_BEV'] = pd.cut(gdf_nonzero[BEVmean_column_name], bins=percentiles_all, labels=range(len(percentiles_all) - 1))

    # 绘制数据为0的地块，颜色设置为白色
    gdf_zero.plot(ax=ax, color='white', legend=False)
    gdf_nonzero.plot(column='bin_BEV', ax=ax, cmap=cmap, legend=False)  
    base_map.plot(ax=ax, color='none', edgecolor='black', linewidth=2)

    # 自定义块状图例
    legend_elements = [Patch(facecolor='white', edgecolor='black', label='0')]  
    legend_elements.extend([Patch(facecolor=cmap(j), edgecolor='black', label=f'{int(percentiles_all[j - 1])}-{int(percentiles_all[j])}')
                        for j in range(1, len(percentiles_all) - 1)])  

    ax.legend(handles=legend_elements, title="Population Density Range\nUnit: Person/KM2", loc='upper right', fontsize=25)
    plt.title(title, fontsize=TitleSize, fontname='Times New Roman', fontweight='bold') 
    
    output_file_path = os.path.join(folder_name, 'Geometrically Spaced', f"{os.path.splitext(shp_file)[0]}.png")
    plt.savefig(output_file_path, dpi=30, bbox_inches='tight')
    plt.close()
