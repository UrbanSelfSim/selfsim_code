import os
import re
import pickle
import pandas as pd
import numpy as np
import geopandas as gpd
import networkx as nx
import osmnx as ox
from tqdm import tqdm
from math import exp
from shapely.geometry import Point
from geopy.distance import geodesic
from shapely import wkt
import gc  # Import garbage collection module
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import os
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# sys.argv = ['person_acc_calculation_selfsim_every_year.ipynb', 'full_daily_plan', 'home']

# 定义全局参数和路径
GRAPH_PATHS = {
    'Private Vehicle': 'Scenarios/Beijing/Daily Plan/Road/nyc_drive_simple.graphml',
    'Two_wheel': 'Scenarios/Beijing/Daily Plan/Road/nyc_bike_simple.graphml',
    'Walk': 'Scenarios/Beijing/Daily Plan/Road/nyc_combined_walk_bike_simple.graphml',
    'Taxi': 'Scenarios/Beijing/Daily Plan/Road/nyc_drive_simple.graphml',
    'For-Hire Vehicle': 'Scenarios/Beijing/Daily Plan/Road/nyc_drive_simple.graphml',
    'Subway': 'Scenarios/Beijing/Daily Plan/Road/subway_graph.pkl',
    'Bus': 'Scenarios/Beijing/Daily Plan/Road/bus_network_graph.pkl'
}

OUTPUT_BASE_PATH = 'Mobility and Accessibility/ACC Calculation/Output'

PURPOSES = ['home', 'work', 'leisure', 'shopping', 'education']
MODES = ['Private Vehicle', 'Two_wheel', 'Walk', 'Taxi', 'For-Hire Vehicle', 'Subway', 'Bus']
DAY_TYPES = ['weekday', 'weekend']

# 定义速度和费用参数
PARAMS = {
    'Private Vehicle': {
        'speed_m_per_s': 30 * 1000 / 3600,  # 30 km/h
        'fuel_cost_per_km': 0.5,  # $0.5/km
        'base_fare': None,
        'fare_per_km': None
    },
    'Two_wheel': {
        'speed_m_per_s': 15 * 1000 / 3600,  # 15 km/h
        'fuel_cost_per_km': 0,  # 无直接燃油费用
        'base_fare': None,
        'fare_per_km': None
    },
    'Walk': {
        'speed_m_per_s': 5 * 1000 / 3600,  # 5 km/h
        'fuel_cost_per_km': 0,  # 无直接燃油费用
        'base_fare': None,
        'fare_per_km': None
    },
    'Taxi': {
        'speed_m_per_s': 40 * 1000 / 3600,  # 40 km/h
        'fuel_cost_per_km': None,
        'base_fare': 3.0,  # $3 基础费用
        'fare_per_km': 1.5  # $1.5/km
    },
    'For-Hire Vehicle': {  # 假设与Taxi相同
        'speed_m_per_s': 40 * 1000 / 3600,
        'fuel_cost_per_km': None,
        'base_fare': 3.0,
        'fare_per_km': 1.5
    },
    'Subway': {  # 地铁有特殊处理
        'speed_km_per_h': 30, # 30 km/h
        'fuel_cost_per_km': None,
        'base_fare': 2.75,  # 单程地铁票价
        'fare_per_km': None
    },
    'Bus': {  # 公交有特殊处理
        'speed_km_per_h': 12, # 12 km/h
        'fuel_cost_per_km': None,
        'base_fare': 2.75,  # 公交首程票价
        'fare_per_km': None
    }
}

def load_trip_data():
    """加载工作日和周末的计划数据，并转换坐标为Point对象。"""
        
    housing_data = pd.read_csv('Mobility and Accessibility/ACC Calculation/Input/housing_processed.csv')
    housing_data['live_location'] = housing_data['live_location'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else None)

    person_data = pd.read_csv('Mobility and Accessibility/ACC Calculation/Input/person_processed.csv')
    person_data['work_point'] = person_data['work_point'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else None)

    weekday_plan_path = 'Mobility and Accessibility/ACC Calculation/Input/weekday_plan_with_location.csv'
    weekend_plan_path = ''

    # Check if the file exists and read data
    if os.path.exists(weekday_plan_path):
        weekday_plan = pd.read_csv(weekday_plan_path)
    else:
        weekday_plan = None
        print(f"警告: {weekday_plan_path} 文件不存在。")

    if os.path.exists(weekend_plan_path):
        weekend_plan = pd.read_csv(weekend_plan_path)
    else:
        weekend_plan = None
        print(f"警告: {weekend_plan_path} 文件不存在。")

    # Convert coordinates to Point objects
    # Convert coordinates to Point objects
    if weekday_plan is not None:
        weekday_plan['tt_o_xy'] = weekday_plan['tt_o_xy'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else None)
        weekday_plan['tt_d_xy'] = weekday_plan['tt_d_xy'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else None)

    if weekend_plan is not None:
        weekend_plan['tt_o_xy'] = weekend_plan['tt_o_xy'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else None)
        weekend_plan['tt_d_xy'] = weekend_plan['tt_d_xy'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else None)

    return weekday_plan, weekend_plan, housing_data, person_data

def load_graph_for_mode(mode):
    """加载并返回指定模式的网络图。"""
    path = GRAPH_PATHS.get(mode)
    if not path:
        print(f"未定义模式 {mode} 的路径。")
        return None
    
    if mode in ['Subway', 'Bus']:
        # Subway and bus graphs are preprocessed and loaded with pickle
        try:
            with open(path, 'rb') as f:
                graph = pickle.load(f)
            print(f"{mode} 网络图已从pickle文件加载。")
        except Exception as e:
            print(f"无法从pickle文件加载 {mode} 网络图: {e}")
            return None
    else:
        # Other modes use GraphML files
        try:
            graph = ox.load_graphml(path)
            graph = ox.project_graph(graph)
            print(f"{mode} 网络图已从GraphML文件加载并投影。")
        except Exception as e:
            print(f"无法从GraphML文件加载 {mode} 网络图: {e}")
            return None
    
    return graph


def find_nearest_node(graph, point):
    """在网络图中找到与给定点最近的节点。"""
    try:
        return ox.distance.nearest_nodes(graph, X=point.x, Y=point.y)
    except Exception as e:
        print(f"找到最近节点失败: {e}")
        return None
    
def sanitize_purpose(purpose):
    """
    清洗目的名称，移除或替换文件名中不允许的特殊字符。
    这里将 '/' 替换为 '_', 你可以根据需要进行调整。
    """
    # Replace all non-alphanumeric characters with underscores or other safe characters
    return re.sub(r'[^\w\-]', '_', purpose)

def calculate_vehicle_journey(journeys, journey_results, daytype, graph, params, purpose):
    """计算车辆行程的函数。"""
    for idx, row in tqdm(journeys.iterrows(), total=len(journeys), desc=f"Processing {daytype}{purpose} Private Vehicle Journeys"):
        try:
            origin = row['tt_o_xy']
            destination = row['tt_d_xy']

            points_gdf = gpd.GeoDataFrame(geometry=[origin, destination], crs='EPSG:4326')
            points_proj = points_gdf.to_crs(graph.graph['crs'])
            origin_proj, destination_proj = points_proj.geometry.iloc[0], points_proj.geometry.iloc[1]

            orig_node = find_nearest_node(graph, origin_proj)
            dest_node = find_nearest_node(graph, destination_proj)

            if orig_node is None or dest_node is None:
                raise ValueError("无法找到起点或终点的最近节点。")

            route_length = nx.shortest_path_length(graph, orig_node, dest_node, weight='length')

            if route_length == 0:
                continue

            time_in_seconds = route_length / params['speed_m_per_s']
            time_in_minutes = time_in_seconds / 60
            cost_in_dollars = (route_length / 1000) * params['fuel_cost_per_km']

            # 记录结果到journey_results
            journey_results.append({
                'Unnamed: 0': row['Unnamed: 0'],
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': time_in_minutes,
                'cost': cost_in_dollars
            })

        except Exception as e:
            print(f"行程 {idx} 计算失败: {e}")
            journey_results.append({
                'Unnamed: 0': row['Unnamed: 0'],
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': None,
                'cost': None
            })

def calculate_bike_journey(journeys, journey_results, daytype, graph, params, purpose):
    """计算自行车行程的函数。"""
    for idx, row in tqdm(journeys.iterrows(), total=len(journeys), desc=f"Processing {daytype}{purpose}Two_wheel Journeys"):
        try:
            origin = row['tt_o_xy']
            destination = row['tt_d_xy']

            points_gdf = gpd.GeoDataFrame(geometry=[origin, destination], crs='EPSG:4326')
            points_proj = points_gdf.to_crs(graph.graph['crs'])
            origin_proj, destination_proj = points_proj.geometry.iloc[0], points_proj.geometry.iloc[1]

            orig_node = find_nearest_node(graph, origin_proj)
            dest_node = find_nearest_node(graph, destination_proj)

            if orig_node is None or dest_node is None:
                raise ValueError("无法找到起点或终点的最近节点。")

            route_length = nx.shortest_path_length(graph, orig_node, dest_node, weight='length')

            if route_length == 0:
                continue

            time_in_seconds = route_length / params['speed_m_per_s']
            time_in_minutes = time_in_seconds / 60
            cost_in_dollars = 0  # No direct fuel cost for biking

            # 记录结果到journey_results
            journey_results.append({
                'Unnamed: 0': row['Unnamed: 0'],
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': time_in_minutes,
                'cost': cost_in_dollars
            })

        except Exception as e:
            print(f"行程 {idx} 计算失败: {e}")
            journey_results.append({
                'Unnamed: 0': row['Unnamed: 0'],
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': None,
                'cost': None
            })

def calculate_walk_journey(journeys, journey_results, daytype, graph, params, purpose):
    """计算步行行程的函数，并定期保存结果。"""

    for idx, row in tqdm(journeys.iterrows(), total=len(journeys), desc=f"Processing {daytype}{purpose} Walk Journeys"):
        try:
            origin = row['tt_o_xy']
            destination = row['tt_d_xy']

            points_gdf = gpd.GeoDataFrame(geometry=[origin, destination], crs='EPSG:4326')
            points_proj = points_gdf.to_crs(graph.graph['crs'])
            origin_proj, destination_proj = points_proj.geometry.iloc[0], points_proj.geometry.iloc[1]

            orig_node = find_nearest_node(graph, origin_proj)
            dest_node = find_nearest_node(graph, destination_proj)

            if orig_node is None or dest_node is None:
                raise ValueError("无法找到起点或终点的最近节点。")

            route_length = nx.shortest_path_length(graph, orig_node, dest_node, weight='length')

            if route_length == 0:
                continue

            time_in_seconds = route_length / params['speed_m_per_s']
            time_in_minutes = time_in_seconds / 60
            cost_in_dollars = 0  # No direct fuel cost for walking

            # 记录结果到journey_results
            journey_results.append({
                'Unnamed: 0': row['Unnamed: 0'],
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': time_in_minutes,
                'cost': cost_in_dollars
            })

        except Exception as e:
            print(f"行程 {idx} 计算失败: {e}")
            journey_results.append({
                'Unnamed: 0': row['Unnamed: 0'],
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': None,
                'cost': None
            })

def calculate_taxi_journey(journeys, journey_results, daytype, graph, params, purpose):
    """计算出租车行程的函数。"""
    for idx, row in tqdm(journeys.iterrows(), total=len(journeys), desc=f"Processing {daytype}{purpose} Taxi Journeys"):
        try:
            origin = row['tt_o_xy']
            destination = row['tt_d_xy']

            points_gdf = gpd.GeoDataFrame(geometry=[origin, destination], crs='EPSG:4326')
            points_proj = points_gdf.to_crs(graph.graph['crs'])
            origin_proj, destination_proj = points_proj.geometry.iloc[0], points_proj.geometry.iloc[1]

            orig_node = find_nearest_node(graph, origin_proj)
            dest_node = find_nearest_node(graph, destination_proj)

            if orig_node is None or dest_node is None:
                raise ValueError("无法找到起点或终点的最近节点。")

            route_length = nx.shortest_path_length(graph, orig_node, dest_node, weight='length')

            if route_length > 100000:  # 100公里
                print(f"行程 {idx}: 路径长度异常 {route_length:.2f} 米，跳过此行程")
                continue

            time_in_seconds = route_length / params['speed_m_per_s']
            time_in_minutes = time_in_seconds / 60
            cost_in_dollars = params['base_fare'] + (route_length / 1000) * params['fare_per_km']

            # 记录结果到journey_results
            journey_results.append({
                'Unnamed: 0': row['Unnamed: 0'],
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': time_in_minutes,
                'cost': cost_in_dollars
            })

        except Exception as e:
            print(f"行程 {idx} 计算失败: {e}")
            journey_results.append({
                'Unnamed: 0': row['Unnamed: 0'],
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': None,
                'cost': None
            })

def calculate_for_hire_vehicle_journey(journeys, journey_results, daytype, graph, params, purpose):
    """计算For-Hire Vehicle行程的函数，假设与出租车相同。"""
    calculate_taxi_journey(journeys, journey_results, daytype, graph, params, purpose)

# 定义寻找最近地铁站的函数
def find_nearest_station(point, stations):
    min_distance = float('inf')
    nearest_station = None
    point = Point(point)
    for station, details in stations.items():
        station_point = details['point']
        # 修正地理距离的坐标顺序
        distance = geodesic((point.y, point.x), (station_point.y, station_point.x)).meters
        if distance < min_distance:
            min_distance = distance
            nearest_station = station
    return nearest_station

def calculate_route_and_cost(from_point, to_point, stations, G, grasmere_station, bay_ridge_station, params):
    """计算地铁路径的最短路径、距离、时间和费用。"""
    try:
        # 找到起点和终点的最近地铁站
        from_station = find_nearest_station(from_point, stations)
        to_station = find_nearest_station(to_point, stations)

        if from_station is None or to_station is None:
            print("无法找到起点或终点的最近地铁站。")
            return None, 0, 0

        # 使用 Dijkstra 算法找到最短路径
        path = nx.dijkstra_path(G, source=from_station, target=to_station, weight='weight')
        total_time = 0
        total_cost = 0

        is_cross_sea = False  # 标记是否经过跨海连接

        # 遍历路径，逐段计算距离、时间和费用
        for i in range(len(path) - 1):
            segment_distance = geodesic(path[i], path[i + 1]).kilometers

            # 判断是否是跨海段（根据特定站点）
            if (grasmere_station in (path[i], path[i + 1])) and (bay_ridge_station in (path[i], path[i + 1])):
                is_cross_sea = True
                # Taxi fare for cross-sea segment
                taxi_base_fare = 3.0
                taxi_per_km_fare = 1.5
                taxi_speed = 20.0  # km/h

                segment_cost = taxi_base_fare + segment_distance * taxi_per_km_fare
                segment_time = (segment_distance / taxi_speed) * 60  # 分钟

                total_cost += segment_cost
                total_time += segment_time
            else:
                # 地铁段，计算时间
                segment_time = (segment_distance / params['speed_km_per_h']) * 60  # 分钟
                total_time += segment_time

        # 计算总费用
        if is_cross_sea:
            # 跨海需要两次地铁票价
            total_cost += params['base_fare'] * 2
        else:
            # 普通地铁路径只需要一次地铁票价
            total_cost += params['base_fare']

        # # 打印路径是否为跨海路径
        # if is_cross_sea:
        #     print("跨海路径")
        # else:
        #     print("纯地铁路径")

        return path, total_time, total_cost

    except nx.NetworkXNoPath:
        print("无法在给定的地铁站之间找到路径。")
        return None, 0, 0
    
def calculate_subway_journey(journeys, journey_results, daytype, subway_graph, stations, grasmere_station, bay_ridge_station, params, purpose):
    """计算地铁行程的函数。"""
    for idx, row in tqdm(journeys.iterrows(), total=len(journeys), desc=f"Processing {daytype}{purpose} Subway Journeys"):
        try:
            origin = row['tt_o_xy']
            destination = row['tt_d_xy']

            path, time_in_minutes, cost_in_dollars = calculate_route_and_cost(
                origin, destination, stations, subway_graph, grasmere_station, bay_ridge_station, params
            )

            # 记录结果到journey_results
            journey_results.append({
                'Unnamed: 0': row['Unnamed: 0'],
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': time_in_minutes,
                'cost': cost_in_dollars
            })

        except Exception as e:
            print(f"行程 {idx} 计算失败: {e}")
            journey_results.append({
                'Unnamed: 0': row['Unnamed: 0'],
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': None,
                'cost': None
            })

# 找到最近的公交站点
def find_nearest_stop(point, G):
    min_dist = float('inf')
    nearest_stop = None
    for stop in G.nodes:
        stop_point = Point(stop)
        dist = point.distance(stop_point)
        if dist < min_dist:
            min_dist = dist
            nearest_stop = stop
    return nearest_stop

# def find_nearest_stop(point, G):
#     min_dist = float('inf')
#     nearest_stop = None
#     for stop in G.nodes:
#         stop_data = G.nodes[stop]
#         stop_point = Point(stop_data['x'], stop_data['y'])  # 根据实际属性名调整
#         dist = geodesic((point.y, point.x), (stop_point.y, stop_point.x)).meters
#         if dist < min_dist:
#             min_dist = dist
#             nearest_stop = stop
#     return nearest_stop

# 提取线路编号函数
def extract_route_number(route_name):
    match = re.match(r'NYCB - (\w+)', route_name)
    if match:
        return match.group(1)
    return route_name

# 移除路径中连续重复的节点
def clean_path(path):
    cleaned_path = []
    for i in range(len(path)):
        if i == 0 or path[i] != path[i - 1]:
            cleaned_path.append(path[i])
    return cleaned_path

# 计算最短路径、时间和票价（考虑只能在公交站点换乘）
def calculate_shortest_path_with_stop_restriction(G, origin, destination, params):
    # 找到最近的起点和终点站
    origin_stop = find_nearest_stop(origin, G)
    destination_stop = find_nearest_stop(destination, G)
    
    # 计算最短路径
    path = nx.shortest_path(G, source=origin_stop, target=destination_stop, weight='weight')
    
    # 清理路径以去除冗余节点
    path = clean_path(path)
    
    # 计算总路程
    total_distance = nx.shortest_path_length(G, source=origin_stop, target=destination_stop, weight='weight')
    
    # 假设平均公交速度为 12 公里/小时，时间 = 距离 / 速度
    total_time = (total_distance / 1000) / params['speed_km_per_h'] * 60  # 转换为分钟
    
    # 计算票价，初始化为首程票价
    total_fare = 2.75
    current_route_numbers = set(extract_route_number(route_name) for route_name in G.edges[path[0], path[1]]['name'])
    
    # 存储路径中涉及的线路编号
    route_numbers_set = set(current_route_numbers)

    # 用于存储上一个站点位置
    last_stop = origin_stop if G.nodes[origin_stop].get('type') == 'stop' else None

    for i in range(1, len(path) - 1):
        u, v = path[i], path[i + 1]
        edge_data = G.get_edge_data(u, v)
        route_numbers = set(extract_route_number(name) for name in edge_data.get('name', [])) if edge_data else set()
        
        # 如果当前节点是公交站点
        if G.nodes[u].get('type') == 'stop':
            # 记录当前路径的线路编号
            route_numbers_set.update(route_numbers)

            # 只有在站点处换乘才增加票价
            if last_stop and not current_route_numbers.intersection(route_numbers):
                total_fare += 2.75
                current_route_numbers = route_numbers
            last_stop = u  # 更新上一个站点位置

    return path, total_distance, total_time, total_fare


def calculate_bus_journey(journeys, journey_results, daytype, bus_graph, params, purpose):
    """计算公交行程的函数。"""
    for idx, row in tqdm(journeys.iterrows(), total=len(journeys), desc=f"Processing {daytype}{purpose} Bus Journeys"):
        try:
            origin = row['tt_o_xy']
            destination = row['tt_d_xy']

            path, distance, time_in_minutes, cost_in_dollars = calculate_shortest_path_with_stop_restriction(bus_graph, origin, destination, params)

            # 记录结果到journey_results
            journey_results.append({
                'Unnamed: 0': row['Unnamed: 0'],
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': time_in_minutes,
                'cost': cost_in_dollars
            })

        except Exception as e:
            print(f"行程 {idx} 计算失败: {e}")
            journey_results.append({
                'Unnamed: 0': row['Unnamed: 0'],
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': None,
                'cost': None
            })

def merge_output_csvs(output_base_path, day_types, purposes, housing, person):
    """
    读取 output_base_path 下各 daytype 和 purpose_label 目录中的所有 CSV 文件，
    并将它们合并为一个 DataFrame，存储在一个字典中。
    
    Args:
        output_base_path (str): 输出基础路径。
        day_types (list): 天类型列表，例如 ['weekday', 'weekend']。
        purposes (list): 目的列表，例如 ['Home', 'Work', 'Social_Recreation_Shop']。
    
    Returns:
        dict: 合并后的 DataFrame 字典，键为 '{purpose_label.lower()}_{daytype}_plan'。
    """
    merged_plans = {}

    for daytype in day_types:
        for purpose_label in purposes:
            # 构建输出目录路径
            output_dir = os.path.join(output_base_path, daytype, purpose_label)
            
            if not os.path.isdir(output_dir):
                logging.warning(f"目录不存在: {output_dir}。跳过...")
                key = f"{purpose_label.lower()}_{daytype}_plan"
                merged_plans[key] = None
                continue
            
            # 获取该目录下所有 CSV 文件的路径
            csv_files = [os.path.join(output_dir, file) for file in os.listdir(output_dir) if file.endswith('.csv')]
            
            if not csv_files:
                logging.warning(f"没有找到 CSV 文件在目录: {output_dir}。跳过...")
                continue
            
            # 读取并合并所有 CSV 文件
            dataframes = []
            for file in csv_files:
                try:
                    df = pd.read_csv(file)
                    dataframes.append(df)
                    logging.info(f"已读取文件: {file}")
                except Exception as e:
                    logging.error(f"读取文件 {file} 失败: {e}")
            
            if dataframes:
                try:
                    merged_df = pd.concat(dataframes, ignore_index=True)
                    merged_plan = pd.merge(merged_df, housing, on='hh_id', how='left')
                    merged_plan['Cc'] = ((merged_plan['cost'] / merged_plan['hh_income']))* 100
                    merged_plan['Ct'] = merged_plan['time']

                    merged_plan['fx'] = np.exp(-(1.95 * merged_plan['Ct'] + 2.39 * merged_plan['Cc']))
  
                    key = f"{purpose_label.lower()}_{daytype}_plan"
                    merged_plans[key] = merged_plan

                    logging.info(f"已合并并存储 DataFrame: {key}")
                except Exception as e:
                    logging.error(f"合并文件失败在目录 {output_dir}: {e}")
            else:
                logging.warning(f"没有有效的数据框可以合并在目录: {output_dir}。")
    
    return merged_plans

def assign_merged_plans(merged_plans):
    """
    将合并后的 DataFrame 赋值给全局变量。
    
    Args:
        merged_plans (dict): 包含合并后 DataFrame 的字典。
    """
    for key, df in merged_plans.items():
        # 生成变量名，例如 'home_weekday_plan'
        var_name = key
        globals()[var_name] = df
        logging.info(f"已将 DataFrame 赋值为变量: {var_name}")
    print("已将所有合并后的 DataFrame 赋值为全局变量。")

def process_plan_dataframe(df):
    if df is None:
        print("警告: 计划数据为空，跳过处理。")
        return None
    
    # 选择必要的列
    df_selected = df[['hh_id','hh_people','tt_o_xy', 'fx']].copy()
    
    # Group and aggregate
    df_grouped = df_selected.groupby('hh_id', as_index=False).agg(
        hh_people=('hh_people', 'first'),
        tt_o_xy=('tt_o_xy', 'first'), 
        fx_total=('fx', 'sum')
    )
 
    # Keep necessary columns
    df_result = df_grouped[['hh_id','tt_o_xy', 'fx_total','hh_people']].copy()

    df_result['fx_total'] = df_result['fx_total']/df_result['hh_people']   

    return df_result

def process_fx(weekday_plan_fx, weekend_plan_fx):
    # 计算一周的时间段
    if weekend_plan_fx is not None:
        merged_plan = pd.merge(
            weekday_plan_fx, 
            weekend_plan_fx, 
            on=['hh_id'], 
            how='outer',
            suffixes=('_weekday', '_weekend')
        )

        merged_plan['fx_weekday'] = merged_plan['fx_total_weekday'] * 5
        merged_plan['fx_weekend'] = merged_plan['fx_total_weekend'] * 2

        merged_plan = merged_plan.fillna(0)

        merged_plan['fx'] = (merged_plan['fx_weekday'] + merged_plan['fx_weekend'])/7

        merged_plan_result = merged_plan[['hh_id', 'tt_o_xy_weekday', 'fx', 'hh_people']].copy()

        merged_plan_result = merged_plan_result.rename(columns={'tt_o_xy_weekday': 'location'})
        

    else:
        # 如果 weekend_plan_fx 为 None，只使用 weekday_plan_fx
        merged_plan = weekday_plan_fx.copy()
        merged_plan['fx'] = merged_plan['fx_total'] * 5/7

        merged_plan_result = merged_plan[['hh_id', 'tt_o_xy', 'fx','hh_people']].copy()

        merged_plan_result = merged_plan_result.rename(columns={'tt_o_xy': 'location'})
    
    

    return merged_plan_result

def full_daily_plan(acc_type):
    print("Executing full daily plan...")
    weekday_plan, weekend_plan, housing_data, person_data = load_trip_data()
    housing_data = housing_data[['hh_id', 'hh_income', 'hh_people','live_location']]
    person_data = person_data[['unique_id', 'hh_id', 'job','ff_id', 'work_point']]
    
    # 加载地铁站点信息
    with open('Scenarios/Beijing/Daily Plan/Road/stations.pkl', 'rb') as f:
        stations = pickle.load(f)
    
    # 定义Grasmere 和 Bay Ridge - 95 St 的坐标
    grasmere_actual_coords = (-74.091, 40.603)
    bay_ridge_actual_coords = (-74.030, 40.622)
    
    # 找到最近的地铁站节点
    grasmere_station = find_nearest_station(grasmere_actual_coords, stations)
    bay_ridge_station = find_nearest_station(bay_ridge_actual_coords, stations)
    
    print(f"Grasmere station: {grasmere_station}")
    print(f"Bay Ridge station: {bay_ridge_station}")
    
    if acc_type == 'home':

        # Iterate through all transport modes
        for mode in MODES:
            print(f"正在处理交通方式: {mode}")
            
            # Load the graph for the current mode
            graph = load_graph_for_mode(mode)
            
            if graph is None:
                print(f"无法加载 {mode} 的网络图。跳过此交通方式。")
                continue
            
            # Iterate through all day types
            for daytype in DAY_TYPES:
                if daytype == 'weekday':
                    plan = weekday_plan.copy() if weekday_plan is not None else None
                else:
                    plan = weekend_plan.copy() if weekend_plan is not None else None
                
                # 如果 plan 为空，跳过该天类型
                if plan is None:
                    print(f"警告: {daytype} 数据不存在，跳过该天类型处理。")
                    continue
    
                # Filter valid trips
                journeys = plan[(plan['tt_mode'] == mode)]

                # Exclude trips with missing origin or destination coordinates
                journeys = journeys[journeys['tt_o_xy'].notna() & journeys['tt_d_xy'].notna()]
                
                if journeys.empty:
                    print(f"没有 {daytype} {mode} 的行程。跳过...")
                    continue
                
                # Get corresponding parameters
                params = PARAMS.get(mode)
                
                # Initialize list to store results
                journey_results = []

                purpose_label = 'all_purpose'

                # Call corresponding calculation function
                if mode == 'Private Vehicle':
                    calculate_vehicle_journey(journeys, journey_results, daytype, graph, params, purpose_label)
                elif mode == 'Two_wheel':
                    calculate_bike_journey(journeys, journey_results, daytype, graph, params, purpose_label)
                elif mode == 'Walk':
                    calculate_walk_journey(journeys, journey_results, daytype, graph, params, purpose_label)
                elif mode == 'Taxi' or mode == 'For-Hire Vehicle':
                    calculate_taxi_journey(journeys, journey_results, daytype, graph, params, purpose_label)
                elif mode == 'Subway':
                    calculate_subway_journey(journeys, journey_results, daytype, graph, stations, grasmere_station, bay_ridge_station, params, purpose_label)
                elif mode == 'Bus':
                    calculate_bus_journey(journeys, journey_results, daytype, graph, params, purpose_label)
                else:
                    print(f"未知的交通方式: {mode}。跳过...")
                    continue
                
                output_dir = os.path.join(OUTPUT_BASE_PATH, daytype, purpose_label)
                os.makedirs(output_dir, exist_ok=True)
                # Modify filename to include daytype, purpose, and mode
                save_path = os.path.join(output_dir, f'{daytype}_{purpose_label}_plan_with_fx_{mode.lower()}.csv')

                if journey_results:
                    journey_df = pd.DataFrame(journey_results)
                    journey_df.to_csv(save_path, index=False)
                    print(f"已保存 {daytype} {purpose_label} {mode} 行程的计算结果到 {save_path}")
                else:
                    print(f"没有计算结果可保存 for {daytype} {purpose_label} {mode}.")
            
            # Release memory of the graph after processing
            del graph
            gc.collect()
            print(f"{mode} 的网络图已释放内存。\n")
        
        print("所有行程计算完成，并保存为包含 fx 列的 CSV 文件。")

        # Call merge function
        merged_plans = merge_output_csvs(OUTPUT_BASE_PATH, DAY_TYPES, ['all_purpose'], housing_data, person_data)

        # Assign merged DataFrame to global variables
        assign_merged_plans(merged_plans)

        home_weekday_plan = merged_plans.get('all_purpose_weekday_plan')
        home_weekend_plan = merged_plans.get('all_purpose_weekend_plan')
        home_weekday_plan_fx = process_plan_dataframe(home_weekday_plan)
        home_weekend_plan_fx = process_plan_dataframe(home_weekend_plan)
        home_fx = process_fx(home_weekday_plan_fx, home_weekend_plan_fx)

        # 将 'hh_id' 列转换为字符串格式，先做 split 操作
        home_fx['hh_id'] = home_fx['hh_id'].astype(str)
        # Split 'hh_id' using str.split and extract components
        home_fx[['hh_id', 'RID']] = home_fx['hh_id'].str.split('_', n=1, expand=True)
        # Fill NaN in 'RID' if '_' is missing
        home_fx['RID'] = home_fx['RID'].fillna(-1)
        # 转换 'hh_id' 和 'RID' 列为整数类型
        home_fx['hh_id'] = home_fx['hh_id'].astype(int)
        home_fx['RID'] = home_fx['RID'].astype(int)

        output_dir = os.path.join(OUTPUT_BASE_PATH, 'acc_result', 'person_based')
        os.makedirs(output_dir, exist_ok=True)
        home_save_path = os.path.join(output_dir, f'full_home.csv')

        home_fx.to_csv(home_save_path, index=False)
        print(f"已保存 home acc")

    elif acc_type == 'work':
        
        person_data = person_data[person_data['ff_id'].notna() & person_data['work_point'].notna()]
        combine_data = person_data.merge(housing_data[['hh_id', 'hh_income', 'hh_people','live_location']], on='hh_id', how='left')
        weekday_plan_data_select = weekday_plan[weekday_plan['tt_d_purpose'] == 'work']
        weekday_plan_data_select = weekday_plan_data_select[['hh_id','unique_id','tt_mode']]
        weekday_plan_data_select = weekday_plan_data_select.drop_duplicates(subset=['hh_id','unique_id'],keep='first')

        # 通过 'unique_id' 合并 weekday_plan_data_select 和 combine_data
        combine_data = pd.merge(combine_data, weekday_plan_data_select[['hh_id','unique_id','tt_mode']], on=['unique_id', 'hh_id'], how='left')
      
        combine_data.rename(columns={'work_point': 'tt_o_xy', 'live_location': 'tt_d_xy'}, inplace=True)
        combine_data['Unnamed: 0'] = combine_data.index


        # Iterate through all transport modes
        for mode in MODES:
            print(f"正在处理交通方式: {mode}")
            
            # Load the graph for the current mode
            graph = load_graph_for_mode(mode)
            
            if graph is None:
                print(f"无法加载 {mode} 的网络图。跳过此交通方式。")
                continue
            
            plan = combine_data.copy()

            # Filter valid trips
            journeys = plan[(plan['tt_mode'] == mode)]

            # Exclude trips with missing origin or destination coordinates
            journeys = journeys[journeys['tt_o_xy'].notna() & journeys['tt_d_xy'].notna()]
            
            if journeys.empty:
                print(f"没有 {daytype} {mode} 的行程。跳过...")
                continue
            
            # Get corresponding parameters
            params = PARAMS.get(mode)
            
            # Initialize list to store results
            journey_results = []

            purpose_label = 'work'
            daytype = 'weekday'

            # Call corresponding calculation function
            if mode == 'Private Vehicle':
                calculate_vehicle_journey(journeys, journey_results, daytype, graph, params, purpose_label)
            elif mode == 'Two_wheel':
                calculate_bike_journey(journeys, journey_results, daytype, graph, params, purpose_label)
            elif mode == 'Walk':
                calculate_walk_journey(journeys, journey_results, daytype, graph, params, purpose_label)
            elif mode == 'Taxi' or mode == 'For-Hire Vehicle':
                calculate_taxi_journey(journeys, journey_results, daytype, graph, params, purpose_label)
            elif mode == 'Subway':
                calculate_subway_journey(journeys, journey_results, daytype, graph, stations, grasmere_station, bay_ridge_station, params, purpose_label)
            elif mode == 'Bus':
                calculate_bus_journey(journeys, journey_results, daytype, graph, params, purpose_label)
            else:
                print(f"未知的交通方式: {mode}。跳过...")
                continue
            
            output_dir = os.path.join(OUTPUT_BASE_PATH, daytype, purpose_label)
            os.makedirs(output_dir, exist_ok=True)
            # Modify filename to include daytype, purpose, and mode
            save_path = os.path.join(output_dir, f'{daytype}_{purpose_label}_plan_with_fx_{mode.lower()}.csv')

            if journey_results:
                journey_df = pd.DataFrame(journey_results)
                journey_df.to_csv(save_path, index=False)
                print(f"已保存 {daytype} {purpose_label} {mode} 行程的计算结果到 {save_path}")
            else:
                print(f"没有计算结果可保存 for {daytype} {purpose_label} {mode}.")
            
            # Release memory of the graph after processing
            del graph
            gc.collect()
            print(f"{mode} 的网络图已释放内存。\n")
        
        print("所有行程计算完成，并保存为包含 fx 列的 CSV 文件。")

        # Call merge function
        merged_plans = merge_output_csvs(OUTPUT_BASE_PATH, ['weekday'], ['work'], housing_data, person_data)

        # Assign merged DataFrame to global variables
        assign_merged_plans(merged_plans)

        work_weekday_plan = merged_plans.get('work_weekday_plan')

        person_work_weekday_plan = pd.merge(combine_data, work_weekday_plan[['hh_id','unique_id', 'cost', 'time']], on=['hh_id','unique_id'], how='left')
        person_work_weekday_plan['Cc'] = ((person_work_weekday_plan['cost'] / person_work_weekday_plan['hh_income']))* 100
        person_work_weekday_plan['Ct'] = person_work_weekday_plan['time'] 

        person_work_weekday_plan['fx'] = np.exp(-(1.95 * person_work_weekday_plan['Ct'] + 2.39 * person_work_weekday_plan['Cc']))
        
        # 选择必要的列
        person_work_weekday_plan_selected = person_work_weekday_plan[['job','ff_id', 'tt_o_xy', 'fx']].copy()
        
        # Group and aggregate
        person_work_weekday_plan_grouped = person_work_weekday_plan_selected.groupby(['job', 'ff_id'], as_index=False).agg(
            tt_o_xy=('tt_o_xy', 'first'),  # 保留每个 'ff_id' 的第一个 'tt_o_xy' 值
            fx_total=('fx', 'sum'),         
            employee_number=('ff_id', 'count')   # 统计 'ff_id' 的计数
        )
        
        # Keep necessary columns
        person_work_weekday_plan_result = person_work_weekday_plan_grouped[['job','ff_id','tt_o_xy', 'fx_total', 'employee_number']].copy()
        
        person_work_weekday_plan_result['fx_total'] = person_work_weekday_plan_result['fx_total']/person_work_weekday_plan_result['employee_number']

        # 将 'ff_id' 列转换为字符串格式，先做 split 操作
        person_work_weekday_plan_result['ff_id'] = person_work_weekday_plan_result['ff_id'].astype(str)
        # Split 'hh_id' using str.split and extract components
        person_work_weekday_plan_result[['ff_id', 'FID']] = person_work_weekday_plan_result['ff_id'].str.split('_', n=1, expand=True)
        # 如果没有 '_', 'FID' 会是 NaN，填充为 0
        person_work_weekday_plan_result['FID'] = person_work_weekday_plan_result['FID'].fillna(-1)
        # 转换 'ff_id' 和 'FID' 列为整数类型
        person_work_weekday_plan_result['ff_id'] = person_work_weekday_plan_result['ff_id'].astype(int)
        person_work_weekday_plan_result['FID'] = person_work_weekday_plan_result['FID'].astype(int)

        output_dir = os.path.join(OUTPUT_BASE_PATH, 'acc_result', 'person_based')
        os.makedirs(output_dir, exist_ok=True)
        work_save_path = os.path.join(output_dir, f'full_work.csv')

        person_work_weekday_plan_result.to_csv(work_save_path, index=False)
        print(f"已保存 work acc")

    else:
        print("无效输入，请输入 'home' 或 'work'")

def simple_daily_plan(acc_type):
    print("Executing simple daily plan...")
    
    # 加载数据
    weekday_plan, weekend_plan, housing_data, person_data = load_trip_data()
    housing_data = housing_data[['hh_id', 'live_location']]
    person_data = person_data[['unique_id', 'hh_id', 'job','ff_id', 'work_point']]
    person_data = person_data[person_data['ff_id'].notna() & person_data['work_point'].notna()]

    combine_data = person_data.merge(housing_data[['hh_id', 'live_location']], on='hh_id', how='left')
    combine_data['home_work_distance'] = combine_data.apply(
        lambda row: row['work_point'].distance(row['live_location']) if row['work_point'] and row['live_location'] else None, axis=1)
    
    if acc_type == 'home':
        # 按照 'hh_id' 分组并计算 'home_work_distance' 的平均值
        hh_avg = combine_data.groupby('hh_id')['home_work_distance'].mean().reset_index()
        hh_avg['fx'] = np.exp(-hh_avg['home_work_distance'])
        
        # Save the result
        output_dir = os.path.join(OUTPUT_BASE_PATH, 'acc_result', 'person_based')
        os.makedirs(output_dir, exist_ok=True)
        home_save_path = os.path.join(output_dir, f'simple_home.csv')
        hh_avg.to_csv(home_save_path, index=False)
        print(f"已保存 home acc")

    elif acc_type == 'work':
        # 按照 'ff_id' 分组并计算 'home_work_distance' 的平均值
        ff_avg = combine_data.groupby('ff_id')['home_work_distance'].mean().reset_index()
        ff_avg['fx'] = np.exp(-ff_avg['home_work_distance'])
        
        # Save the result
        output_dir = os.path.join(OUTPUT_BASE_PATH, 'acc_result', 'person_based')
        os.makedirs(output_dir, exist_ok=True)
        work_save_path = os.path.join(output_dir, f'simple_work.csv')
        ff_avg.to_csv(work_save_path, index=False)
        print(f"已保存 work acc")

    else:
        print("无效输入，请输入 'home' 或 'work'")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Choose the type of daily plan.")
    
    # Add command-line arguments
    parser.add_argument('plan_type', choices=['simple_daily_plan', 'full_daily_plan'],
                        help="Specify the daily plan type to execute.")
    parser.add_argument('acc_type', choices=['home', 'work'], help="Specify the account type to calculate.")

    # Parse command-line arguments
    args = parser.parse_args()

    # Retrieve parsed arguments
    plan_type = args.plan_type
    acc_type = args.acc_type

    # Execute different logic based on plan_type
    if plan_type == 'simple_daily_plan':
        simple_daily_plan(acc_type)
    elif plan_type == 'full_daily_plan':
        full_daily_plan(acc_type)

if __name__ == "__main__":
    main()
