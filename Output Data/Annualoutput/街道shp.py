import numpy as np
import pandas as pd
import pyproj
import os
import shutil

import geopandas as gpd
import matplotlib.pyplot as plt
from datetime import datetime
from shapely.geometry import Point


from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import Normalize
from matplotlib.colorbar import ColorbarBase
#%%


years = list(range(2010, 2054))
output_folder = os.path.join(os.getcwd(), "csv街道图中转")
os.makedirs(output_folder, exist_ok=True)


for year in years:
    csv_file_path = f"residences{year}year.csv"
    if os.path.isfile(csv_file_path):  
        df = pd.read_csv(csv_file_path)
        
        # 新增rmbcap列，其值为House-price除以capacity
        df['Rrmbcap'] = df['House-price'] / df['capacity']
        # 过滤掉包含缺失值或负数的行
        df = df[(df['Rrmbcap'].notna()) & (df['Rrmbcap'] >= 0)]
        
        # 将rmbcap列中的非有限值替换为默认值（例如0）
        df['Rrmbcap'] = df['Rrmbcap'].replace([np.inf, -np.inf], 0)
        #df = df[(df['Rrmbcap'].notna()) & (df['Rrmbcap'] >= 0)]
        # 将rmbcap列转换为整数类型
        df['Rrmbcap'] = df['Rrmbcap'].astype(int)
        output_file_path = os.path.join(output_folder, f"residences{year}year.csv")
        df.to_csv(output_file_path, index=False)
        print(f"处理完成并保存到 {output_file_path}")
    else:
        print(f"")

years = list(range(2010, 2054))
output_folder = os.path.join(os.getcwd(), "csv街道图中转")
os.makedirs(output_folder, exist_ok=True)


for year in years:
    csv_file_path = f"OBs{year}year.csv"
    if os.path.isfile(csv_file_path):  
        df = pd.read_csv(csv_file_path)
        

        df['Ormbcap'] = df['ob-price'] / df['capacity']

        df = df[(df['Ormbcap'].notna()) & (df['Ormbcap'] >= 0)]
        

        df['Ormbcap'] = df['Ormbcap'].replace([np.inf, -np.inf], 0)
        #df = df[(df['Ormbcap'].notna()) & (df['Ormbcap'] >= 0)]
        

        df['Ormbcap'] = df['Ormbcap'].astype(int)
        output_file_path = os.path.join(output_folder, f"OBs{year}year.csv")
        df.to_csv(output_file_path, index=False)
        print(f"处理完成并保存到 {output_file_path}")
    else:
        print(f"")

#%%
current_time = datetime.now()
plt.rcParams.update({'font.size': 20})
folder_name = "shp_Result_output_time_" + current_time.strftime("%Y-%m-%d-%H-%M-%S")

try:
    os.mkdir(folder_name)
    print(f"已创建文件夹：{folder_name}")
except FileExistsError:
    print(f"{folder_name} 文件夹已存在")

base_map_path = "basemap/深圳街道.shp"
base_map = gpd.read_file(base_map_path)

#residences

residences_price = {}

years = list(range(2010, 2054))  


output_folder = os.path.join(os.getcwd(), "residences街道图中转")
os.makedirs(output_folder, exist_ok=True)


for year in years:
    csv_file_path = f"csv街道图中转/residences{year}year.csv"
    
    if os.path.isfile(csv_file_path):  
        df = pd.read_csv(csv_file_path)
        

        x = df['x-coordinate']
        y = df['y-coordinate']
        

        geometry = [Point(xy) for xy in zip(x, y)]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        

        output_shapefile = os.path.join(output_folder, f"Housing Price {year} year.shp")
        
        gdf.to_file(output_shapefile)
        
        print(f"{year}已转换WGS84，保存在 {output_shapefile}。")
    else:
        print()


input_folder = "residences街道图中转"  
output_folder = "residences街道图中转/第一步图像相交结果" 


os.makedirs(output_folder, exist_ok=True)

base_map_path = "basemap/深圳街道.shp"
base_map = gpd.read_file(base_map_path)


for filename in os.listdir(input_folder):
    if filename.endswith(".shp"):  
        input_file_path = os.path.join(input_folder, filename)
        gdf_points = gpd.read_file(input_file_path)
        gdf_points = gdf_points.reset_index(drop=True)
        joined_data = gpd.sjoin(gdf_points, base_map, how="left", op="within")
        
        # 检查有点没有到任何面
        unmatched_points = joined_data[joined_data['index_right'].isnull()]
        
        if not unmatched_points.empty:
            print(f"文件 {filename} 中有 {len(unmatched_points)} 个点没有面。")
        
        # 移除不到面的点
        joined_data = joined_data.dropna(subset=['index_right'])
        # 计算每个面内点数据的属性字段的平均值（此处为SHP字段的名称）
        result = joined_data.groupby('index_right')['Rrmbcap'].mean().reset_index()
        result_gdf = gpd.GeoDataFrame(result, geometry=base_map.geometry.loc[result['index_right']].reset_index(drop=True), crs=base_map.crs)
        
        # 处理没有点的面平均值设置为0
        missing_face_ids = set(base_map.index) - set(result_gdf['index_right'])
        missing_faces = gpd.GeoDataFrame({'index_right': list(missing_face_ids), 'Rrmbcap': [0] * len(missing_face_ids)}, geometry=base_map.geometry.loc[list(missing_face_ids)].reset_index(drop=True), crs=base_map.crs)

        result_gdf = pd.concat([result_gdf, missing_faces])

        output_file_path = os.path.join(output_folder, filename)
        result_gdf.to_file(output_file_path)
        
        print(f"处理完成：{filename}，结果已保存到 {output_file_path}")

print("所有文件处理完成。")



shp_folder = "residences街道图中转\第一步图像相交结果"  
gdf_list = []

shp_files = [f for f in os.listdir(shp_folder) if f.endswith('.shp')]

for shp_file in shp_files:
    shp_file_path = os.path.join(shp_folder, shp_file)
    gdf = gpd.read_file(shp_file_path)
    gdf_list.append(gdf)


all_residences_price = []

for gdf in gdf_list:
    price_column_name = "Rrmbcap"  
    if price_column_name in gdf.columns:
        all_residences_price.extend(gdf[price_column_name])

#计算所有年份的租金数据的总体范围
max_price_all_years = max(all_residences_price)
min_price_all_years = min(all_residences_price)


num_bins = 8  # 调整分段的数量
price_range_all_years = [min_price_all_years + (max_price_all_years - min_price_all_years) * i / num_bins for i in range(num_bins + 1)]  # 不要改变这一行


for i, (shp_file, gdf) in enumerate(zip(shp_files, gdf_list)):
    fig, ax = plt.subplots(1, 1, figsize=(40, 40))

    cmap = plt.get_cmap('YlGn', num_bins)  

    gdf.plot(column=price_column_name, ax=ax, cmap=cmap, legend=False)  

    # 自定义块状图例
    for j in range(num_bins):
        ax.fill_between([], [], color=cmap(j), label=f'{int(price_range_all_years[j])}-{int(price_range_all_years[j+1])}')

    # 显示图例
    ax.legend(title="Housing Price Range\nUnit: RMB/Capacity", loc='upper right',fontsize=25)
    plt.title(f"{os.path.splitext(shp_file)[0]}",fontsize=35)
    
    output_file_path = os.path.join(folder_name, f"{os.path.splitext(shp_file)[0]}.png")
    plt.savefig(output_file_path, dpi=300, bbox_inches='tight')
    plt.close()

print("")

#%%

#OBS

base_map_path = "basemap/深圳街道.shp"
base_map = gpd.read_file(base_map_path)


OBs_price = {}

years = list(range(2010, 2054))  


output_folder = os.path.join(os.getcwd(), "OBs街道图中转")
os.makedirs(output_folder, exist_ok=True)


for year in years:
    csv_file_path = f"csv街道图中转/OBs{year}year.csv"
    
    if os.path.isfile(csv_file_path):  
        df = pd.read_csv(csv_file_path)
        

        x = df['x-coordinate']
        y = df['y-coordinate']
        

        geometry = [Point(xy) for xy in zip(x, y)]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        

        output_shapefile = os.path.join(output_folder, f"OBs Price {year} year.shp")
        
        gdf.to_file(output_shapefile)
        
        print(f"{year}已转换WGS84，保存在 {output_shapefile}。")
    else:
        print()


input_folder = "OBs街道图中转"  
output_folder = "OBs街道图中转/第一步图像相交结果"  


os.makedirs(output_folder, exist_ok=True)

base_map_path = "basemap/深圳街道.shp"
base_map = gpd.read_file(base_map_path)


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

        result = joined_data.groupby('index_right')['Ormbcap'].mean().reset_index()
        result_gdf = gpd.GeoDataFrame(result, geometry=base_map.geometry.loc[result['index_right']].reset_index(drop=True), crs=base_map.crs)
        

        missing_face_ids = set(base_map.index) - set(result_gdf['index_right'])
        missing_faces = gpd.GeoDataFrame({'index_right': list(missing_face_ids), 'Ormbcap': [0] * len(missing_face_ids)}, geometry=base_map.geometry.loc[list(missing_face_ids)].reset_index(drop=True), crs=base_map.crs)

        result_gdf = pd.concat([result_gdf, missing_faces])

        output_file_path = os.path.join(output_folder, filename)
        result_gdf.to_file(output_file_path)
        
        print(f"处理完成：{filename}，结果已保存到 {output_file_path}")

print("所有文件处理完成。")



shp_folder = "OBs街道图中转\第一步图像相交结果"  
gdf_list = []

shp_files = [f for f in os.listdir(shp_folder) if f.endswith('.shp')]

for shp_file in shp_files:
    shp_file_path = os.path.join(shp_folder, shp_file)
    gdf = gpd.read_file(shp_file_path)
    gdf_list.append(gdf)


all_obs_price = []

for gdf in gdf_list:
    price_column_name = "Ormbcap"  
    if price_column_name in gdf.columns:
        all_obs_price.extend(gdf[price_column_name])

#计算所有年份的租金数据的总体范围
max_obs_price_all_years = max(all_obs_price)
min_obs_price_all_years = min(all_obs_price)


num_bins = 8  # 调整分段的数量
price_range_all_years = [min_obs_price_all_years + (max_obs_price_all_years - min_obs_price_all_years) * i / num_bins for i in range(num_bins + 1)]  # 不要改变这一行


for i, (shp_file, gdf) in enumerate(zip(shp_files, gdf_list)):
    fig, ax = plt.subplots(1, 1, figsize=(40, 40))

    cmap = plt.get_cmap('YlGnBu', num_bins)  

    gdf.plot(column=price_column_name, ax=ax, cmap=cmap, legend=False)  

    # 自定义块状图例
    for j in range(num_bins):
        ax.fill_between([], [], color=cmap(j), label=f'{int(price_range_all_years[j])}-{int(price_range_all_years[j+1])}')

    ax.legend(title=" Office Building Price Range\nUnit: RMB/Capacity", loc='upper right',fontsize=25)
    plt.title(f"{os.path.splitext(shp_file)[0]}",fontsize=35)
    
    output_file_path = os.path.join(folder_name, f"{os.path.splitext(shp_file)[0]}.png")
    plt.savefig(output_file_path, dpi=300, bbox_inches='tight')
    plt.close()

print("")

#%%

#Firm


base_map_path = "basemap/深圳街道.shp"
base_map = gpd.read_file(base_map_path)


firms_staff = {}

years = list(range(2010, 2054))  


output_folder = os.path.join(os.getcwd(), "firms街道图中转")
os.makedirs(output_folder, exist_ok=True)


for year in years:
    csv_file_path = f"firms{year}year.csv"
    
    if os.path.isfile(csv_file_path):  
        df = pd.read_csv(csv_file_path)
        

        x = df['x-coordinate']
        y = df['y-coordinate']
        

        geometry = [Point(xy) for xy in zip(x, y)]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        

        output_shapefile = os.path.join(output_folder, f"firms Employees {year} year.shp")
        
        gdf.to_file(output_shapefile)
        
        print(f"{year}已转换WGS84，保存在 {output_shapefile}。")
    else:
        print()


input_folder = "firms街道图中转"  
output_folder = "firms街道图中转/第一步图像相交结果" 


os.makedirs(output_folder, exist_ok=True)

base_map_path = "basemap/深圳街道.shp"
base_map = gpd.read_file(base_map_path)

# "深圳街道.shp"中的"area"字段
base_map['AREA'] = base_map['AREA'].astype(float)  # 浮点数类型

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

        result = joined_data.groupby('index_right')['staff'].sum().reset_index()
        result_gdf = gpd.GeoDataFrame(result, geometry=base_map.geometry.loc[result['index_right']].reset_index(drop=True), crs=base_map.crs)
        

        missing_face_ids = set(base_map.index) - set(result_gdf['index_right'])
        missing_faces = gpd.GeoDataFrame({'index_right': list(missing_face_ids), 'staff': [0] * len(missing_face_ids)}, geometry=base_map.geometry.loc[list(missing_face_ids)].reset_index(drop=True), crs=base_map.crs)

        result_gdf = pd.concat([result_gdf, missing_faces])
        result_gdf['AREA'] = base_map['AREA'].loc[result_gdf['index_right']].reset_index(drop=True)
        result_gdf['Stfmean'] = result_gdf['staff'] / result_gdf['AREA']
        output_file_path = os.path.join(output_folder, filename)
        result_gdf.to_file(output_file_path)
        


                
        print(f"处理完成：{filename}，结果已保存到 {output_file_path}")

print("所有文件处理完成。")



shp_folder = "firms街道图中转\第一步图像相交结果"  
gdf_list = []

shp_files = [f for f in os.listdir(shp_folder) if f.endswith('.shp')]

for shp_file in shp_files:
    shp_file_path = os.path.join(shp_folder, shp_file)
    gdf = gpd.read_file(shp_file_path)
    gdf_list.append(gdf)


all_firms_Stfmean = []

for gdf in gdf_list:
    Stfmean_column_name = "Stfmean"  
    if Stfmean_column_name in gdf.columns:
        all_firms_Stfmean.extend(gdf[Stfmean_column_name])


max_firms_Stfmean_all_years = max(all_firms_Stfmean)
min_firms_Stfmean_all_years = min(all_firms_Stfmean)


num_bins = 5  # 调整分段的数量
Stfmean_range_all_years = [min_firms_Stfmean_all_years + (max_firms_Stfmean_all_years - min_firms_Stfmean_all_years) * i / num_bins for i in range(num_bins + 1)]  # 不要改变这一行


for i, (shp_file, gdf) in enumerate(zip(shp_files, gdf_list)):
    fig, ax = plt.subplots(1, 1, figsize=(40, 40))

    cmap = plt.get_cmap('YlOrBr', num_bins) 

    gdf.plot(column=Stfmean_column_name, ax=ax, cmap=cmap, legend=False)  

    # 自定义块状图例
    for j in range(num_bins):
        ax.fill_between([], [], color=cmap(j), label=f'{int(Stfmean_range_all_years[j])}-{int(Stfmean_range_all_years[j+1])}')


    legend = ax.legend(title=" Firms Staff Range\nUnit: 1000people/KM2", loc='upper right', fontsize=25)

    plt.title(f"{os.path.splitext(shp_file)[0]}",fontsize=35)
    
    output_file_path = os.path.join(folder_name, f"{os.path.splitext(shp_file)[0]}.png")
    plt.savefig(output_file_path, dpi=300, bbox_inches='tight')
    plt.close()

print("")

#%%

base_map_path = "basemap/深圳街道.shp"
base_map = gpd.read_file(base_map_path)


people_density = {}

years = list(range(2010, 2054))  


output_folder = os.path.join(os.getcwd(), "people街道图中转")
os.makedirs(output_folder, exist_ok=True)


for year in years:
    csv_file_path = f"people{year}year.csv"
    
    if os.path.isfile(csv_file_path): 
        df = pd.read_csv(csv_file_path)
        

        x = df['x-coordinate']
        y = df['y-coordinate']
        

        geometry = [Point(xy) for xy in zip(x, y)]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        

        output_shapefile = os.path.join(output_folder, f"people {year} year.shp")
        
        gdf.to_file(output_shapefile)
        
        print(f"{year}已转换WGS84，保存在 {output_shapefile}。")
    else:
        print()


input_folder = "people街道图中转"  
output_folder = "people街道图中转/第一步图像相交结果"  


os.makedirs(output_folder, exist_ok=True)

base_map_path = "basemap/深圳街道.shp"
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
        result_gdf['Peomean'] = result_gdf['people-ID'] / result_gdf['AREA']
        output_file_path = os.path.join(output_folder, filename)
        result_gdf.to_file(output_file_path)

        print(f"处理完成：{filename}，结果已保存到 {output_file_path}")

print("")



shp_folder = "people街道图中转\第一步图像相交结果"  
gdf_list = []

shp_files = [f for f in os.listdir(shp_folder) if f.endswith('.shp')]

for shp_file in shp_files:
    shp_file_path = os.path.join(shp_folder, shp_file)
    gdf = gpd.read_file(shp_file_path)
    gdf_list.append(gdf)


all_people_Peomean = []

for gdf in gdf_list:
    Peomean_column_name = "Peomean"  
    if Peomean_column_name in gdf.columns:
        all_people_Peomean.extend(gdf[Peomean_column_name])


max_people_Peomean_all_years = max(all_people_Peomean)
min_people_Peomean_all_years = min(all_people_Peomean)


num_bins = 10  
Peomean_range_all_years = [min_people_Peomean_all_years + (max_people_Peomean_all_years - min_people_Peomean_all_years) * i / num_bins for i in range(num_bins + 1)]  # 不要改变这一行


for i, (shp_file, gdf) in enumerate(zip(shp_files, gdf_list)):
    fig, ax = plt.subplots(1, 1, figsize=(40, 40))

    cmap = plt.get_cmap('Reds', num_bins)  

    gdf.plot(column=Peomean_column_name, ax=ax, cmap=cmap, legend=False)  


    for j in range(num_bins):
        ax.fill_between([], [], color=cmap(j), label=f'{int(Peomean_range_all_years[j])}-{int(Peomean_range_all_years[j+1])}')


    ax.legend(title=" Population Density\nUnit: 1000people/KM2", loc='upper right',fontsize=25)#图块大小
    plt.title(f"{os.path.splitext(shp_file)[0]}",fontsize=35)#图例fontsize标题大小
    
    output_file_path = os.path.join(folder_name, f"{os.path.splitext(shp_file)[0]}.png")
    plt.savefig(output_file_path, dpi=300, bbox_inches='tight')
    plt.close()

print("")

#%%

current_directory = os.getcwd()


csv_files = [file for file in os.listdir(current_directory) if file.endswith('year.csv')]


if not os.path.exists(folder_name):
    os.makedirs(folder_name)


for csv_file in csv_files:
    source_path = os.path.join(current_directory, csv_file)
    destination_path = os.path.join(folder_name, csv_file)
    shutil.move(source_path, destination_path)

print("")
#%%


for item in os.listdir(current_directory):
    item_path = os.path.join(current_directory, item)
    
    # 检查"中转"
    if os.path.isdir(item_path) and "街道图中转" in item:
        
        # 删除非空文件夹
        for root, dirs, files in os.walk(item_path, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                os.rmdir(dir_path)
        
        # 删除空文件夹
        os.rmdir(item_path)

print("已结束所有过程，并清理，源CSV文件已移动到目标文件夹")
