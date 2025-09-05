#Parts of the code in this model were generated with the assistance of AI and subsequently revised and validated by the author

import os
import re
import pickle
import pandas as pd
import numpy as np
import geopandas as gpd
import networkx as nx
import osmnx as ox
# from tqdm import tqdm
from math import exp
from shapely.geometry import Point
from geopy.distance import geodesic
from shapely import wkt
import gc
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import os
import pandas as pd
import logging
from functools import lru_cache
from diskcache import Cache
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

NETLOGO = r"C:/Program Files/NetLogo 6.4.0/NetLogo_Console.exe"
MODEL   = r"Run_SelfSim0322.nlogo"

def run_netlogo(experiment_name):
    cmd = [
        NETLOGO,
        "--headless",
        "--model", MODEL,
        "--experiment", experiment_name
    ]
    print(f"Running NetLogo experiment {experiment_name} …")
    subprocess.run(cmd, check=True)
    print(f"Finished NetLogo experiment {experiment_name}")


os.makedirs('Mobility and Accessibility/cache/graph_cache',        exist_ok=True)
GRAPH_CACHE = Cache(
    directory='Mobility and Accessibility/cache/graph_cache',
    size_limit=5 * 1024**3, 
    eviction_policy='least-recently-used'
)


################################################################################
# Set parameters for multiprocessing and chunking
# Define the max_workers parameter for each mode of transportation
MAX_WORKERS = {
    # The road network for walking takes up more memory, so its value needs to be set lower than other transport modes to avoid crashes
    'Walk': 4,
    'default': 12
}
CHUNK_SIZE = 10000
####################################################################################

def get_graph_paths(city):
    base_path = f'Scenarios/{city}/Road'
    return {
        'Private Vehicle': f'{base_path}/private_vehicle.graphml',
        'Two_wheel': f'{base_path}/two_wheel.graphml',
        'Walk': f'{base_path}/walk.graphml',
        'Taxi': f'{base_path}/taxi.graphml',
        'For-Hire Vehicle': f'{base_path}/for_hire_vehicle.graphml',
        'Subway': f'{base_path}/subway.pkl',
        'Bus': f'{base_path}/bus.pkl'
    }

INPUT_CURRENT_PATH = 'Output Data'
OUTPUT_CURRENT_PATH = 'Output Data'


PURPOSES = ['home', 'work', 'leisure', 'shopping', 'education']
MODES = ['Private Vehicle', 'Two_wheel', 'Walk', 'Taxi', 'For-Hire Vehicle', 'Subway', 'Bus']
DAY_TYPES = ['weekday', 'weekend']

# Define speed and cost parameters
def load_params_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    params = {}

    for _, row in df.iterrows():
        mode = row['mode']
        params[mode] = {
            'speed_m_per_s': row['speed_kmh'] * 1000 / 3600,
            'fuel_cost_per_km': row['fuel_cost_per_km'],
            'base_fare': row['base_fare'],
            'fare_per_km': row['fare_per_km']
        }

    return params

# Example usage:
# PARAMS = load_params_from_csv('Scenarios/newyork/Settings/Accessibility/params.csv')


def load_trip_data():
    """load housing and person data"""
    housing_file_path = os.path.join(INPUT_CURRENT_PATH, 'housing_processed.csv')
    housing_file_path  = housing_file_path.replace("\\", "/")
    housing_data = pd.read_csv(housing_file_path)
    housing_data['live_location'] = housing_data['live_location'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else None)

    person_data_path = os.path.join(INPUT_CURRENT_PATH, 'person_processed.csv')
    person_data_path  = person_data_path.replace("\\", "/")
    person_data = pd.read_csv(person_data_path)
    person_data.columns = person_data.columns.str.strip()  
    person_data['work_point'] = person_data['work_point'].apply(lambda x: wkt.loads(x) if isinstance(x, str) and x.strip() else None)

    return housing_data, person_data


# 2. Unified disk cache loading function
def load_graph_for_mode(mode):
    """Load and return the network graph for the specified mode, using diskcache to cache the result."""
    path = GRAPH_PATHS.get(mode)
    if not path:
        print(f"undefined {mode} path")
        return None

    abs_path = os.path.abspath(path)
    # If the graph object is already in the cache, return it directly.
    if abs_path in GRAPH_CACHE:
        graph = GRAPH_CACHE[abs_path]
        print(f"{mode} network graph has been loaded from the disk cache.")
    else:
        if mode in ['Subway', 'Bus']:
            try:
                with open(path, 'rb') as f:
                    graph = pickle.load(f)
                print(f"{mode} network graph has been loaded from the pickle.")
            except Exception as e:
                print(f"cannot load {mode} network graph has from the pickle: {e}")
                return None
        else:
            try:
                graph = ox.load_graphml(path)
                graph = ox.project_graph(graph)
                print(f"{mode} network graph has been loaded from the GraphML.")
            except Exception as e:
                print(f"cannot load {mode} network graph has from the pickle: {e}")
                return None
            graph.graph['path'] = abs_path
        GRAPH_CACHE[abs_path] = graph
    return graph

#########################################Pre-caching optimization######################################################
# Define global cache dictionary
NEAREST_NODE_CACHE = {}

def find_nearest_node(graph, point):
    key = (id(graph), round(point.x, 6), round(point.y, 6))
    
    if key in NEAREST_NODE_CACHE:
        return NEAREST_NODE_CACHE[key]
    
    try:
        node = ox.distance.nearest_nodes(graph, X=point.x, Y=point.y)
        NEAREST_NODE_CACHE[key] = node
        return node
    except Exception as e:
        print(f"Failed to find the nearest node: {e}")
        return None
    
##########################
# Global dictionary for storing graph objects, keyed by id(graph)
GRAPH_REGISTRY = {}

def register_graph(graph):
    graph_id = id(graph)
    if graph_id not in GRAPH_REGISTRY:
        GRAPH_REGISTRY[graph_id] = graph
    return graph_id

@lru_cache(maxsize=10000)
def get_shortest_path_length_cached(graph_id, orig_node, dest_node, weight):
    graph = GRAPH_REGISTRY.get(graph_id)
    if graph is None:
        raise ValueError("The specified graph is not registered in GRAPH_REGISTRY.")
    return nx.shortest_path_length(graph, orig_node, dest_node, weight=weight)

def get_shortest_path_length(graph, orig_node, dest_node, weight='length'):
    graph_id = register_graph(graph)
    return get_shortest_path_length_cached(graph_id, orig_node, dest_node, weight)

#########################################Pre-caching optimization######################################################

def sanitize_purpose(purpose):
    return re.sub(r'[^\w\-]', '_', purpose)

def calculate_vehicle_journey(journeys, journey_results, daytype, graph, params, purpose):
    # for idx, row in tqdm(journeys.iterrows(), total=len(journeys), desc=f"Processing {daytype}{purpose} Private Vehicle Journeys"):
    print(f"Processing {daytype}{purpose} Private Vehicle Journeys")
    for idx, row in journeys.iterrows():
        try:
            origin = row['tt_o_xy']
            destination = row['tt_d_xy']

            if origin == destination:
                journey_results.append({
                    
                    'hh_id': row['hh_id'],
                    'unique_id': row['unique_id'],
                    'tt_o_xy': row['tt_o_xy'],
                    'time': 0,
                    'cost': 0
                })
                continue

            points_gdf = gpd.GeoDataFrame(geometry=[origin, destination], crs='EPSG:4326')
            points_proj = points_gdf.to_crs(graph.graph['crs'])
            origin_proj, destination_proj = points_proj.geometry.iloc[0], points_proj.geometry.iloc[1]

            orig_node = find_nearest_node(graph, origin_proj)
            dest_node = find_nearest_node(graph, destination_proj)

            if orig_node is None or dest_node is None:
                raise ValueError("Failed to find the nearest node.")

            # route_length = nx.shortest_path_length(graph, orig_node, dest_node, weight='length')
            route_length = get_shortest_path_length(graph, orig_node, dest_node, weight='length')

            if route_length == 0:
                continue

            time_in_seconds = route_length / params['speed_m_per_s']
            time_in_minutes = time_in_seconds / 60
            cost_in_dollars = params['base_fare'] + (route_length / 1000) * params['fuel_cost_per_km']

            journey_results.append({
                
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': time_in_minutes,
                'cost': cost_in_dollars
            })

        except Exception as e:
            print(f"trip {idx} failed to calculate: {e}")
            journey_results.append({
                
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': None,
                'cost': None
            })

def calculate_bike_journey(journeys, journey_results, daytype, graph, params, purpose):
    # for idx, row in tqdm(journeys.iterrows(), total=len(journeys), desc=f"Processing {daytype}{purpose}Two_wheel Journeys"):
    print(f"Processing {daytype}{purpose} Two_wheel Journeys")
    for idx, row in journeys.iterrows():
        try:
            origin = row['tt_o_xy']
            destination = row['tt_d_xy']

            if origin == destination:
                journey_results.append({
                    
                    'hh_id': row['hh_id'],
                    'unique_id': row['unique_id'],
                    'tt_o_xy': row['tt_o_xy'],
                    'time': 0,
                    'cost': 0
                })
                continue

            points_gdf = gpd.GeoDataFrame(geometry=[origin, destination], crs='EPSG:4326')
            points_proj = points_gdf.to_crs(graph.graph['crs'])
            origin_proj, destination_proj = points_proj.geometry.iloc[0], points_proj.geometry.iloc[1]

            orig_node = find_nearest_node(graph, origin_proj)
            dest_node = find_nearest_node(graph, destination_proj)

            if orig_node is None or dest_node is None:
                raise ValueError("Failed to find the nearest node.")

            route_length = get_shortest_path_length(graph, orig_node, dest_node, weight='length')

            if route_length == 0:
                continue

            time_in_seconds = route_length / params['speed_m_per_s']
            time_in_minutes = time_in_seconds / 60
            cost_in_dollars = params['base_fare'] + (route_length / 1000) * params['fare_per_km']

            journey_results.append({
                
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': time_in_minutes,
                'cost': cost_in_dollars
            })

        except Exception as e:
            print(f"trip {idx} failed to calculate: {e}")
            journey_results.append({
                
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': None,
                'cost': None
            })

def calculate_walk_journey(journeys, journey_results, daytype, graph, params, purpose):
    # for idx, row in tqdm(journeys.iterrows(), total=len(journeys), desc=f"Processing {daytype}{purpose} Walk Journeys"):
    print(f"Processing {daytype}{purpose} Walk Journeys")
    for idx, row in journeys.iterrows():
        try:
            origin = row['tt_o_xy']
            destination = row['tt_d_xy']

            if origin == destination:
                journey_results.append({
                    
                    'hh_id': row['hh_id'],
                    'unique_id': row['unique_id'],
                    'tt_o_xy': row['tt_o_xy'],
                    'time': 0,
                    'cost': 0
                })
                continue

            points_gdf = gpd.GeoDataFrame(geometry=[origin, destination], crs='EPSG:4326')
            points_proj = points_gdf.to_crs(graph.graph['crs'])
            origin_proj, destination_proj = points_proj.geometry.iloc[0], points_proj.geometry.iloc[1]

            orig_node = find_nearest_node(graph, origin_proj)
            dest_node = find_nearest_node(graph, destination_proj)

            if orig_node is None or dest_node is None:
                raise ValueError("Failed to find the nearest node")

            route_length = get_shortest_path_length(graph, orig_node, dest_node, weight='length')

            if route_length == 0:
                continue

            time_in_seconds = route_length / params['speed_m_per_s']
            time_in_minutes = time_in_seconds / 60
            cost_in_dollars = 0

            journey_results.append({
                
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': time_in_minutes,
                'cost': cost_in_dollars
            })

        except Exception as e:
            print(f"trip {idx} failed to calculate: {e}")
            journey_results.append({
                
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': None,
                'cost': None
            })

def calculate_taxi_journey(journeys, journey_results, daytype, graph, params, purpose):
    # for idx, row in tqdm(journeys.iterrows(), total=len(journeys), desc=f"Processing {daytype}{purpose} Taxi Journeys"):
    print(f"Processing {daytype}{purpose} Taxi Journeys")
    for idx, row in journeys.iterrows():
        try:
            origin = row['tt_o_xy']
            destination = row['tt_d_xy']

            if origin == destination:
                journey_results.append({
                    
                    'hh_id': row['hh_id'],
                    'unique_id': row['unique_id'],
                    'tt_o_xy': row['tt_o_xy'],
                    'time': 0,
                    'cost': 0
                })
                continue

            points_gdf = gpd.GeoDataFrame(geometry=[origin, destination], crs='EPSG:4326')
            points_proj = points_gdf.to_crs(graph.graph['crs'])
            origin_proj, destination_proj = points_proj.geometry.iloc[0], points_proj.geometry.iloc[1]

            orig_node = find_nearest_node(graph, origin_proj)
            dest_node = find_nearest_node(graph, destination_proj)

            if orig_node is None or dest_node is None:
                raise ValueError("Failed to find the nearest node")

            # route_length = nx.shortest_path_length(graph, orig_node, dest_node, weight='length')
            route_length = get_shortest_path_length(graph, orig_node, dest_node, weight='length')

            if route_length > 100000:  
                print(f"trip {idx}: bad length {route_length:.2f} m，skip this trip")
                continue

            time_in_seconds = route_length / params['speed_m_per_s']
            time_in_minutes = time_in_seconds / 60
            cost_in_dollars = params['base_fare'] + (route_length / 1000) * params['fare_per_km']

            journey_results.append({
                
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': time_in_minutes,
                'cost': cost_in_dollars
            })

        except Exception as e:
            print(f"trip {idx} failed to calculate: {e}")
            journey_results.append({
                
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': None,
                'cost': None
            })


###############################
# Functions related to nearest subway station caching
###############################

@lru_cache(maxsize=10000)
def cached_find_nearest_station(point_x, point_y, stations_tuple):
    query_point = Point(point_x, point_y)
    min_distance = float('inf')
    nearest_station = None
    for station, coord in stations_tuple:
        station_point = Point(coord)
        distance = geodesic((query_point.y, query_point.x), (station_point.y, station_point.x)).meters
        if distance < min_distance:
            min_distance = distance
            nearest_station = station
    return nearest_station

def find_nearest_station(point, stations):
    if not isinstance(point, Point):
        point = Point(point)
    stations_tuple = tuple(
        (station, (details['point'].x, details['point'].y))
        for station, details in stations.items()
    )
    return cached_find_nearest_station(round(point.x, 6), round(point.y, 6), stations_tuple)

###############################
# Functions related to path, time, and cost caching (subway)
###############################

def convert_point(point):
    if not isinstance(point, Point):
        point = Point(point)
    return (round(point.x, 6), round(point.y, 6))

subway_graph_global = None
stations_global = None

@lru_cache(maxsize=10000)
def cached_calculate_route_and_cost(from_coords, to_coords, base_fare, speed_m_per_s):

    from_point = Point(from_coords)
    to_point = Point(to_coords)
    
    global subway_graph_global, stations_global
    if subway_graph_global is None or stations_global is None:
        raise ValueError("subway_graph_global and stations_global must be initialized")
    
    from_station = find_nearest_station(from_point, stations_global)
    to_station = find_nearest_station(to_point, stations_global)
    
    if from_station is None or to_station is None:
        return None, 0, 0

    try:
        path = nx.dijkstra_path(subway_graph_global, source=from_station, target=to_station, weight='weight')
    except nx.NetworkXNoPath:
        return None, 0, 0

    total_time = 0
    total_cost = 0
    is_cross_sea = False

    for i in range(len(path) - 1):
        segment_distance = geodesic(path[i], path[i + 1]).kilometers

        segment_time = (segment_distance * 1000 / speed_m_per_s) / 60  # minute
        total_time += segment_time

    if is_cross_sea:
        total_cost += base_fare * 2
    else:
        total_cost += base_fare

    return path, total_time, total_cost

def calculate_subway_journey(journeys, journey_results, daytype, subway_graph_input, stations_input, params, purpose):
    global subway_graph_global, stations_global
    subway_graph_global = subway_graph_input
    stations_global = stations_input

    # for idx, row in tqdm(journeys.iterrows(), total=len(journeys), desc=f"Processing {daytype}{purpose} Subway Journeys"):
    print(f"Processing {daytype}{purpose} Subway Journeys")
    for idx, row in journeys.iterrows():
        try:
            origin = row['tt_o_xy']
            destination = row['tt_d_xy']

            if origin == destination:
                journey_results.append({
                    
                    'hh_id': row['hh_id'],
                    'unique_id': row['unique_id'],
                    'tt_o_xy': row['tt_o_xy'],
                    'time': 0,
                    'cost': 0
                })
                continue

            origin_coords = convert_point(origin)
            destination_coords = convert_point(destination)
            
            path, time_in_minutes, cost_in_dollars = cached_calculate_route_and_cost(
                origin_coords, destination_coords,
                params['base_fare'], params['speed_m_per_s']
            )
            
            journey_results.append({
                
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': time_in_minutes,
                'cost': cost_in_dollars
            })
        except Exception as e:
            print(f"trip {idx} failed to calculate: {e}")
            journey_results.append({
                
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': None,
                'cost': None
            })


##################################bus#################

def extract_route_number(route_name):
    match = re.match(r'NYCB - (\w+)', route_name)
    if match:
        return match.group(1)
    return route_name

def clean_path(path):
    cleaned_path = []
    for i in range(len(path)):
        if i == 0 or path[i] != path[i - 1]:
            cleaned_path.append(path[i])
    return cleaned_path

def simplify_bus_graph(G):

    mapping = {node: idx for idx, node in enumerate(G.nodes())}
    G_simple = nx.relabel_nodes(G, mapping)
    for old_node, new_node in mapping.items():
        node_data = G.nodes[old_node]
        if isinstance(node_data, dict) and 'x' in node_data and 'y' in node_data:
            coords = (node_data['x'], node_data['y'])
            pt = Point(coords)
        else:
            try:
                # 尝试将节点本身转换为 Point
                pt = Point(old_node)
                coords = (pt.x, pt.y)
            except Exception as e:
                print(f"cannot convert pt {old_node} to coords: {e}")
                continue
        G_simple.nodes[new_node]['coords'] = coords
        G_simple.nodes[new_node]['point'] = pt

        if isinstance(node_data, dict) and 'type' in node_data:
            G_simple.nodes[new_node]['type'] = node_data['type']
    return G_simple, mapping

@lru_cache(maxsize=10000)
def cached_find_nearest_stop(point_x, point_y, stops_tuple):
    query_point = Point(point_x, point_y)
    min_dist = float('inf')
    nearest_stop = None
    for stop, coord in stops_tuple:
        stop_point = Point(coord)
        dist = query_point.distance(stop_point)
        if dist < min_dist:
            min_dist = dist
            nearest_stop = stop
    return nearest_stop

def find_nearest_stop(point, G):
    if not isinstance(point, Point):
        point = Point(point)
    stops_tuple = tuple(
        (node, G.nodes[node]['coords'])
        for node in G.nodes if 'coords' in G.nodes[node]
    )
    return cached_find_nearest_stop(round(point.x, 6), round(point.y, 6), stops_tuple)

def extract_route_number(route_name):
    import re
    match = re.match(r'NYCB - (\w+)', route_name)
    if match:
        return match.group(1)
    return route_name

def clean_path(path):
    cleaned_path = []
    for i in range(len(path)):
        if i == 0 or path[i] != path[i - 1]:
            cleaned_path.append(path[i])
    return cleaned_path

def calculate_shortest_path_with_stop_restriction(G, origin, destination, params):
    origin_stop = find_nearest_stop(origin, G)
    destination_stop = find_nearest_stop(destination, G)

    path = nx.shortest_path(G, source=origin_stop, target=destination_stop, weight='weight')

    path = clean_path(path)

    total_distance = nx.shortest_path_length(G, source=origin_stop, target=destination_stop, weight='weight')

    total_time = (total_distance / params['speed_m_per_s']) / 60  # minute

    total_fare = params['base_fare']
    current_route_numbers = set(extract_route_number(route_name) for route_name in G.edges[path[0], path[1]]['name'])
    route_numbers_set = set(current_route_numbers)

    last_stop = origin_stop if G.nodes[origin_stop].get('type') == 'stop' else None

    for i in range(1, len(path) - 1):
        u, v = path[i], path[i + 1]
        edge_data = G.get_edge_data(u, v)
        route_numbers = set(extract_route_number(name) for name in edge_data.get('name', [])) if edge_data else set()
        
        if G.nodes[u].get('type') == 'stop':
            route_numbers_set.update(route_numbers)
            if last_stop and not current_route_numbers.intersection(route_numbers):
                total_fare += params['base_fare']
                current_route_numbers = route_numbers
            last_stop = u

    return path, total_distance, total_time, total_fare

def calculate_bus_journey(journeys, journey_results, daytype, bus_graph, params, purpose):

    simplified_bus_graph, mapping = simplify_bus_graph(bus_graph)
    
    # for idx, row in tqdm(journeys.iterrows(), total=len(journeys), desc=f"Processing {daytype}{purpose} Bus Journeys"):
    print(f"Processing {daytype}{purpose} Bus Journeys")
    for idx, row in journeys.iterrows():
        try:
            origin = row['tt_o_xy']
            destination = row['tt_d_xy']

            if origin == destination:
                journey_results.append({
                    
                    'hh_id': row['hh_id'],
                    'unique_id': row['unique_id'],
                    'tt_o_xy': row['tt_o_xy'],
                    'time': 0,
                    'cost': 0
                })
                continue

            path, distance, time_in_minutes, cost_in_dollars = calculate_shortest_path_with_stop_restriction(
                simplified_bus_graph, origin, destination, params
            )

            journey_results.append({
                
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': time_in_minutes,
                'cost': cost_in_dollars
            })

        except Exception as e:
            print(f"trip {idx} failed to calculate: {e}")
            journey_results.append({
                
                'hh_id': row['hh_id'],
                'unique_id': row['unique_id'],
                'tt_o_xy': row['tt_o_xy'],
                'time': None,
                'cost': None
            })



################################
# Chunked reading and multiprocessing parallel processing (core part)
################################

GLOBAL_GRAPH = None
GLOBAL_STATIONS = None


def worker_init(mode, stations=None):

    global GLOBAL_GRAPH, GLOBAL_STATIONS
    GLOBAL_GRAPH = load_graph_for_mode(mode)
    if mode == 'Subway':
        GLOBAL_STATIONS = stations
    logging.info(f"trip {os.getpid()} load {mode} network graph finished")

def worker_process_chunk(chunk, daytype, mode, params, purpose):
    chunk['tt_o_xy'] = chunk['tt_o_xy'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else x)
    chunk['tt_d_xy'] = chunk['tt_d_xy'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else x)

    filtered = chunk[chunk['tt_mode'] == mode]
    if filtered.empty:
        return []
    filtered = filtered[filtered['tt_o_xy'].notna() & filtered['tt_d_xy'].notna()]
    if filtered.empty:
        return []
    journey_results = []
    if mode == 'Private Vehicle':
        calculate_vehicle_journey(filtered, journey_results, daytype, GLOBAL_GRAPH, params, purpose)
    elif mode == 'Two_wheel':
        calculate_bike_journey(filtered, journey_results, daytype, GLOBAL_GRAPH, params, purpose)
    elif mode == 'Walk':
        calculate_walk_journey(filtered, journey_results, daytype, GLOBAL_GRAPH, params, purpose)
    elif mode in ['Taxi', 'For-Hire Vehicle']:
        calculate_taxi_journey(filtered, journey_results, daytype, GLOBAL_GRAPH, params, purpose)
    elif mode == 'Subway':
        calculate_subway_journey(filtered, journey_results, daytype, GLOBAL_GRAPH, GLOBAL_STATIONS, params, purpose)
    elif mode == 'Bus':
        calculate_bus_journey(filtered, journey_results, daytype, GLOBAL_GRAPH, params, purpose)
    return journey_results

def process_mode_in_chunks(input_csv, output_csv, mode, daytype, params, purpose, chunksize=10000, max_workers=4,
                             stations=None):
    if os.path.exists(output_csv):
        os.remove(output_csv)
    
    init_args = (mode,)
    from concurrent.futures import ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=max_workers, initializer=worker_init, initargs=init_args) as executor:
        futures = []
        for chunk in pd.read_csv(input_csv, chunksize=chunksize):
            future = executor.submit(worker_process_chunk, chunk, daytype, mode, params, purpose)
            futures.append(future)
        for future in futures:
            try:
                results = future.result()
                if results:
                    result_df = pd.DataFrame(results)
                    if not os.path.exists(output_csv):
                        result_df.to_csv(output_csv, mode='w', index=False, header=True)
                    else:
                        result_df.to_csv(output_csv, mode='a', index=False, header=False)
                    logging.info(f"write {len(result_df)} to {output_csv}")
            except Exception as e:
                logging.error(f"Error while processing chunk:{e}")

################################
# Functions for merging output, post-processing data, etc.
################################
def merge_output_csvs(output_base_path, day_types, purposes, housing, person):
    merged_plans = {}
    for daytype in day_types:
        for purpose_label in purposes:
            output_dir = os.path.join(output_base_path, daytype, purpose_label)
            if not os.path.isdir(output_dir):
                logging.warning(f"Directory does not exist: {output_dir}.skip...")
                key = f"{purpose_label.lower()}_{daytype}_plan"
                merged_plans[key] = None
                continue
            csv_files = [os.path.join(output_dir, file) for file in os.listdir(output_dir) if file.endswith('.csv')]
            if not csv_files:
                logging.warning(f"No CSV file found in directory: {output_dir}.skip...")
                continue
            dataframes = []
            for file in csv_files:
                try:
                    df = pd.read_csv(file)
                    dataframes.append(df)
                    logging.info(f"File read:{file}")
                except Exception as e:
                    logging.error(f"File read {file} failed: {e}")
            if dataframes:
                try:
                    merged_df = pd.concat(dataframes, ignore_index=True)
                    merged_plan = pd.merge(merged_df, housing, on='hh_id', how='left')

                    merged_plan['VOT'] = merged_plan['hh_income'] / (260 * 8 * merged_plan['hh_people'])
                    merged_plan['Ct_cost'] = merged_plan['time'] * merged_plan['VOT'] / 60
                    merged_plan['fx'] = merged_plan['Ct_cost'] + merged_plan['cost']

                    key = f"{purpose_label.lower()}_{daytype}_plan"
                    merged_plans[key] = merged_plan
                    logging.info(f"DataFrame merged and saved: {key}")
                except Exception as e:
                    logging.error(f"Failed to merge files in directory: {output_dir}: {e}")
            else:
                logging.warning(f"No valid DataFrames to merge in directory: {output_dir}。")
    return merged_plans

def assign_merged_plans(merged_plans):
    for key, df in merged_plans.items():
        var_name = key
        globals()[var_name] = df
        logging.info(f"DataFrame assigned to variable: {var_name}")
    print("All merged DataFrames have been assigned to global variables.")

def process_plan_dataframe(df):
    if df is None:
        print("Warning: Plan data is empty, skipping processing.")
        return None

    df_selected = df[['hh_id','hh_people','tt_o_xy', 'cost', 'time', 'VOT', 'Ct_cost']].copy()
    
    df_grouped = df_selected.groupby('hh_id', as_index=False).agg(
        hh_people=('hh_people', 'first'),
        tt_o_xy=('tt_o_xy', 'first'), 
        Cc_total=('cost', 'sum'),
        time_total=('time', 'sum'),
        VOT=('VOT', 'first'),
        Ct_total=('Ct_cost', 'sum')
    )
    
    df_grouped['fx_total'] = df_grouped['Cc_total'] + df_grouped['Ct_total']

    df_result = df_grouped[['hh_id','tt_o_xy', 'fx_total','hh_people','Cc_total','time_total','VOT','Ct_total']].copy()

    return df_result

def process_fx(weekday_plan_fx, weekend_plan_fx):
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

        merged_plan['Cc_total_weekday'] = merged_plan['Cc_total_weekday'] * 5
        merged_plan['Cc_total_weekend'] = merged_plan['Cc_total_weekend'] * 2

        merged_plan['time_total_weekday'] = merged_plan['time_total_weekday'] * 5
        merged_plan['time_total_weekend'] = merged_plan['time_total_weekend'] * 2

        merged_plan['Ct_total_weekday'] = merged_plan['Ct_total_weekday'] * 5
        merged_plan['Ct_total_weekend'] = merged_plan['Ct_total_weekend'] * 2

        merged_plan = merged_plan.fillna(0)

        merged_plan['fx'] = (merged_plan['fx_weekday'] + merged_plan['fx_weekend'])/7
        merged_plan['fx'] = merged_plan['fx']/merged_plan['hh_people']
        merged_plan['fx'] = np.log1p(merged_plan['fx'])

        merged_plan['Cc_total'] = (merged_plan['Cc_total_weekday'] + merged_plan['Cc_total_weekend'])/7
        merged_plan['time_total'] = (merged_plan['time_total_weekday'] + merged_plan['time_total_weekend'])/7
        merged_plan['Ct_total'] = (merged_plan['Ct_total_weekday'] + merged_plan['Ct_total_weekend'])/7

        merged_plan_result = merged_plan[['hh_id','tt_o_xy', 'fx','hh_people','Cc_total','time_total','VOT','Ct_total']].copy()
        merged_plan_result = merged_plan_result.rename(columns={'tt_o_xy': 'location'})
    else:
        merged_plan = weekday_plan_fx.copy()
        merged_plan['fx'] = merged_plan['fx_total']

        mean_fx = merged_plan.loc[merged_plan['fx'] != 0, 'fx'].mean()
        merged_plan.loc[merged_plan['fx'] == 0, 'fx'] = mean_fx
        merged_plan['fx'] = (1 / merged_plan['fx'])/merged_plan['hh_people']

        merged_plan_result = merged_plan[['hh_id','tt_o_xy', 'fx','hh_people','Cc_total','time_total','VOT','Ct_total']].copy()
        merged_plan_result = merged_plan_result.rename(columns={'tt_o_xy': 'location'})
    return merged_plan_result

################################
#Modified full_daily_plan — uses chunked parallel processing
################################
def full_daily_plan(acc_type, city):
    print("Executing full daily plan...")
    housing_data, person_data = load_trip_data()
    housing_data = housing_data[['hh_id', 'hh_income', 'hh_people','live_location']]
    person_data = person_data[['unique_id', 'hh_id', 'job','ff_id', 'work_point']]

    stations_path = os.path.join(
        "Scenarios",
        city,
        "Road",
        "stations.pkl"
    )
    with open(stations_path, "rb") as f:
        stations = pickle.load(f)
    

    if acc_type == 'home':
        weekday_plan_path = os.path.join(INPUT_CURRENT_PATH, 'weekday_plan_with_location.csv')
        weekday_plan_path  = weekday_plan_path.replace("\\", "/")
        weekend_plan_path = ''
        
        purpose_label = 'all_purpose'
        for mode in MODES:
            for daytype in DAY_TYPES:
                if daytype == 'weekday':
                    input_csv = weekday_plan_path
                else:
                    if not os.path.exists(weekend_plan_path):
                        print(f"warnning: {weekend_plan_path} file does not exist, skip {daytype} ")
                        continue
                    input_csv = weekend_plan_path
                output_dir = os.path.join(OUTPUT_CURRENT_PATH, daytype, purpose_label)
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, f'{daytype}_{purpose_label}_plan_with_fx_{mode.lower()}.csv')
                if mode == 'Subway':
                    process_mode_in_chunks(input_csv, output_file, mode, daytype, PARAMS.get(mode), purpose_label,
                                             chunksize=CHUNK_SIZE, max_workers=MAX_WORKERS.get(mode, MAX_WORKERS['default']),
                                             stations=stations)
                elif mode == 'Walk':
                    process_mode_in_chunks(input_csv, output_file, mode, daytype, PARAMS.get(mode), purpose_label,
                                             chunksize=CHUNK_SIZE, max_workers=MAX_WORKERS.get(mode, MAX_WORKERS['Walk']))
                else:
                    process_mode_in_chunks(input_csv, output_file, mode, daytype, PARAMS.get(mode), purpose_label,
                                             chunksize=CHUNK_SIZE, max_workers=MAX_WORKERS.get(mode, MAX_WORKERS['default']))
                print(f" Processed {daytype} {mode} trips, results saved to {output_file}")
        print("All trip calculations completed and saved as a CSV file containing the 'fx' column.")
        merged_plans = merge_output_csvs(OUTPUT_CURRENT_PATH, DAY_TYPES, ['all_purpose'], housing_data, person_data)
        assign_merged_plans(merged_plans)
        home_weekday_plan = merged_plans.get('all_purpose_weekday_plan')
        home_weekend_plan = merged_plans.get('all_purpose_weekend_plan')
        home_weekday_plan_fx = process_plan_dataframe(home_weekday_plan)
        home_weekend_plan_fx = process_plan_dataframe(home_weekend_plan)
        home_fx = process_fx(home_weekday_plan_fx, home_weekend_plan_fx)
        
        home_fx['hh_id'] = home_fx['hh_id'].astype(str)
        split_df = home_fx['hh_id'].str.split('_', n=1, expand=True)
        if split_df.shape[1] < 2:
            split_df[1] = -1
        home_fx[['hh_id', 'RID']] = split_df
        
        home_fx['RID'] = home_fx['RID'].fillna(-1)
        home_fx['hh_id'] = home_fx['hh_id'].astype(int)
        home_fx['RID'] = home_fx['RID'].astype(int)

        new_order_home = ['hh_id','location', 'fx','hh_people', 'RID','Cc_total','time_total','VOT','Ct_total']
        home_fx = home_fx[new_order_home]

        output_dir = os.path.join(OUTPUT_CURRENT_PATH, 'acc_result', 'person_based')
        os.makedirs(output_dir, exist_ok=True)
        home_save_path = os.path.join(output_dir, f'full_home.csv')
        home_fx.to_csv(home_save_path, index=False)
        print(f"saved home acc")

    elif acc_type == 'work':
        weekday_plan_path = os.path.join(INPUT_CURRENT_PATH, 'weekday_plan_with_location.csv')
        weekday_plan_path  = weekday_plan_path.replace("\\", "/")
        if os.path.exists(weekday_plan_path):
            weekday_plan = pd.read_csv(weekday_plan_path)
            weekday_plan['tt_o_xy'] = weekday_plan['tt_o_xy'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else None)
            weekday_plan['tt_d_xy'] = weekday_plan['tt_d_xy'].apply(lambda x: wkt.loads(x) if isinstance(x, str) else None)
        else:
            weekday_plan = None
            print(f"warnning: {weekday_plan_path} file does not exist")

        person_data = person_data[person_data['ff_id'].notna() & person_data['work_point'].notna()]
        combine_data = person_data.merge(housing_data[['hh_id', 'hh_income', 'hh_people','live_location']], 
                                          on='hh_id', how='left')

        weekday_plan_data_select = weekday_plan[weekday_plan['tt_d_purpose'] == 'work']
        weekday_plan_data_select = weekday_plan_data_select[['hh_id','unique_id','tt_mode']]
        weekday_plan_data_select = weekday_plan_data_select.drop_duplicates(subset=['hh_id','unique_id'], keep='first')
        combine_data = pd.merge(combine_data, weekday_plan_data_select[['hh_id','unique_id','tt_mode']], 
                                 on=['unique_id', 'hh_id'], how='left')
      
        combine_data.rename(columns={'work_point': 'tt_o_xy', 'live_location': 'tt_d_xy'}, inplace=True)

        work_temp_csv = os.path.join(OUTPUT_CURRENT_PATH, 'temp_work_plan.csv')
        combine_data.to_csv(work_temp_csv, index=False)
        print(f"Temporary work CSV file generated:{work_temp_csv}")

        daytype = 'weekday'
        purpose_label = 'work'
        for mode in MODES:
            print(f"processing {daytype} {purpose_label} mode：{mode}")
            output_dir = os.path.join(OUTPUT_CURRENT_PATH, daytype, purpose_label)
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f'{daytype}_{purpose_label}_plan_with_fx_{mode.lower()}.csv')
            if mode == 'Subway':
                process_mode_in_chunks(work_temp_csv, output_file, mode, daytype, PARAMS.get(mode), purpose_label,
                                         chunksize=CHUNK_SIZE, max_workers=MAX_WORKERS.get(mode, MAX_WORKERS['default']),
                                         stations=stations)
            elif mode == 'Walk':
                process_mode_in_chunks(work_temp_csv, output_file, mode, daytype, PARAMS.get(mode), purpose_label,
                                         chunksize=CHUNK_SIZE, max_workers=MAX_WORKERS.get(mode, MAX_WORKERS['Walk']))
            else:
                process_mode_in_chunks(work_temp_csv, output_file, mode, daytype, PARAMS.get(mode), purpose_label,
                                         chunksize=CHUNK_SIZE, max_workers=MAX_WORKERS.get(mode, MAX_WORKERS['default']))
            print(f"processed {daytype} {mode} trip, saved to {output_file}")

        if os.path.exists(work_temp_csv):
            os.remove(work_temp_csv)
        
        print("All work trip calculations completed and saved as a CSV file containing the 'fx' column.")

        merged_plans = merge_output_csvs(OUTPUT_CURRENT_PATH, ['weekday'], ['work'], housing_data, person_data)
        assign_merged_plans(merged_plans)
        work_weekday_plan = merged_plans.get('work_weekday_plan')

        person_work_weekday_plan = pd.merge(combine_data, work_weekday_plan[['hh_id','unique_id', 'cost', 'time']], on=['hh_id','unique_id'], how='left')
        person_work_weekday_plan['VOT'] = person_work_weekday_plan['hh_income'] / (260 * 8 * person_work_weekday_plan['hh_people'])
        person_work_weekday_plan['Ct_cost'] = person_work_weekday_plan['time'] * person_work_weekday_plan['VOT'] /60

        person_work_weekday_plan_selected = person_work_weekday_plan[['job','ff_id', 'tt_o_xy', 'cost', 'time', 'VOT', 'Ct_cost']].copy()
  
        person_work_weekday_plan_grouped = person_work_weekday_plan_selected.groupby(['job', 'ff_id'], as_index=False).agg(
            tt_o_xy=('tt_o_xy', 'first'), 
            Cc_total=('cost', 'sum'),
            time_total=('time', 'sum'),
            VOT=('VOT', 'mean'),
            Ct_total=('Ct_cost', 'sum'),  
            employee_number=('ff_id', 'count') 
        )
        
        person_work_weekday_plan_grouped['fx_total'] = person_work_weekday_plan_grouped['Ct_total'] + person_work_weekday_plan_grouped['Cc_total']

        person_work_weekday_plan_result = person_work_weekday_plan_grouped[['job','ff_id','tt_o_xy', 'fx_total', 'employee_number', 'Cc_total', 'time_total', 'VOT', 'Ct_total']].copy()

        person_work_weekday_plan_result.loc[
            person_work_weekday_plan_result['fx_total'] == 0, 'fx_total'
        ] = 0.01
        mean_fx_total = person_work_weekday_plan_result.loc[person_work_weekday_plan_result['fx_total'] != 0, 'fx_total'].mean()
        person_work_weekday_plan_result.loc[person_work_weekday_plan_result['fx_total'] == 0, 'fx_total'] = mean_fx_total
        person_work_weekday_plan_result['fx_total'] = (1 / person_work_weekday_plan_result['fx_total'])/person_work_weekday_plan_result['employee_number']
        
        person_work_weekday_plan_result['ff_id'] = person_work_weekday_plan_result['ff_id'].astype(str)
        split_df = person_work_weekday_plan_result['ff_id'].str.split('_', n=1, expand=True)
        if split_df.shape[1] < 2:
            split_df[1] = -1
        person_work_weekday_plan_result[['ff_id', 'FID']] = split_df
        person_work_weekday_plan_result['FID'] = person_work_weekday_plan_result['FID'].fillna(-1)
        person_work_weekday_plan_result['ff_id'] = person_work_weekday_plan_result['ff_id'].astype(float).astype(int)
        person_work_weekday_plan_result['FID'] = person_work_weekday_plan_result['FID'].astype(float).astype(int)

        new_order_work = ['job','ff_id','tt_o_xy', 'fx_total', 'employee_number', 'FID', 'Cc_total', 'time_total', 'VOT', 'Ct_total']
        person_work_weekday_plan_result = person_work_weekday_plan_result[new_order_work]
        
        output_dir = os.path.join(OUTPUT_CURRENT_PATH, 'acc_result', 'person_based')
        os.makedirs(output_dir, exist_ok=True)
        work_save_path = os.path.join(output_dir, f'full_work.csv')
        person_work_weekday_plan_result.to_csv(work_save_path, index=False)
        print(f"saved work acc")

    else:
        print("Invalid input, please enter 'home' or 'work'")

def simple_daily_plan(acc_type):
    print("Executing simple daily plan...")
    
    weekday_plan, weekend_plan, housing_data, person_data = load_trip_data()
    housing_data = housing_data[['hh_id', 'live_location']]
    person_data = person_data[['unique_id', 'hh_id', 'job','ff_id', 'work_point']]
    person_data = person_data[person_data['ff_id'].notna() & person_data['work_point'].notna()]

    combine_data = person_data.merge(housing_data[['hh_id', 'live_location']], on='hh_id', how='left')
    combine_data['home_work_distance'] = combine_data.apply(
        lambda row: row['work_point'].distance(row['live_location']) if row['work_point'] and row['live_location'] else None, axis=1)
    
    if acc_type == 'home':
        hh_avg = combine_data.groupby('hh_id')['home_work_distance'].mean().reset_index()
        hh_avg['fx'] = np.exp(-hh_avg['home_work_distance'])
        
        output_dir = os.path.join(OUTPUT_CURRENT_PATH, 'acc_result', 'person_based')
        os.makedirs(output_dir, exist_ok=True)
        home_save_path = os.path.join(output_dir, f'simple_home.csv')
        hh_avg.to_csv(home_save_path, index=False)
        print(f"saved home acc")

    elif acc_type == 'work':
        ff_avg = combine_data.groupby('ff_id')['home_work_distance'].mean().reset_index()
        ff_avg['fx'] = np.exp(-ff_avg['home_work_distance'])
        
        output_dir = os.path.join(OUTPUT_CURRENT_PATH, 'acc_result', 'person_based')
        os.makedirs(output_dir, exist_ok=True)
        work_save_path = os.path.join(output_dir, f'simple_work.csv')
        ff_avg.to_csv(work_save_path, index=False)
        print(f"saved work acc")

    else:
        print("Invalid input, please enter 'home' or 'work'")

def set_stage(year, stage, input_base, output_base):
    global INPUT_CURRENT_PATH, OUTPUT_CURRENT_PATH

    INPUT_CURRENT_PATH  = os.path.join(input_base,  str(year), "Acc Calculation", "Input",stage)
    os.makedirs(INPUT_CURRENT_PATH, exist_ok=True)
    OUTPUT_CURRENT_PATH = os.path.join(output_base, str(year), "Acc Calculation", "Output", stage)
    os.makedirs(OUTPUT_CURRENT_PATH, exist_ok=True)


def full_daily_plan_stage(acc_type, year, city, input_base_path, output_base_path):
    print(f"\n=== Base Year {year} Process {acc_type} Start ===")
    set_stage(year, f"{acc_type}_first_round", input_base_path, output_base_path)
    full_daily_plan(acc_type, city)


def full_pipeline(year, city, input_base_path, output_base_path):

    print(f"\n=== Year {year} Full Process (Go1–Go5 + home/work) Start ===")
    
    # — HOME phase: two Go + home calculations —
    set_stage(year, "home_first_round", input_base_path, output_base_path)
    run_netlogo("Go1") 
    full_daily_plan("home", city)

    set_stage(year, "home_second_round", input_base_path, output_base_path)
    run_netlogo("Go2")
    full_daily_plan("home", city)

    # — WORK phase: two Go + work calculations —
    set_stage(year, "work_first_round", input_base_path, output_base_path)
    run_netlogo("Go3")   
    full_daily_plan("work", city)

    set_stage(year, "work_second_round", input_base_path, output_base_path)
    run_netlogo("Go4")
    full_daily_plan("work", city)

    run_netlogo("Go5")

    print("\n=== Full Process (Go1–Go5 + home/work) Completed ===")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('plan_type',
        choices=['simple_daily_plan','full_daily_plan','full_pipeline'])
    parser.add_argument('--base_year',  type=int, default=2020)
    parser.add_argument('acc_type', nargs='?',
        choices=['home','work'])
    parser.add_argument('--total_years', type=int, default=1,
        help="Number of times to run full_pipeline consecutively, default is 1")
    parser.add_argument('--city', type=str, default='newyork',
        help="City name to select scenario paths (e.g., newyork, beijing)")
    args = parser.parse_args()

    global GRAPH_PATHS
    GRAPH_PATHS = get_graph_paths(args.city)

    global PARAMS
    params_csv = os.path.join(
        'Scenarios',
        args.city,
        'Settings',
        'Accessibility',
        'params.csv'
    )
    PARAMS = load_params_from_csv(params_csv)

    first_year = args.base_year + 1

    output_base_path = 'Output Data'
    input_base_path = 'Output Data'

    if args.plan_type == 'simple_daily_plan':
        simple_daily_plan(args.acc_type)
    elif args.plan_type == 'full_daily_plan':
        full_daily_plan_stage(args.acc_type, args.base_year, args.city, input_base_path, output_base_path)
    elif args.plan_type == 'full_pipeline':
        for i in range(args.total_years):
            current_year = first_year + i
            full_pipeline(current_year, args.city, input_base_path, output_base_path)
        print(f"\n=== Full process completed {args.total_years} times ===")
    else:
        parser.error("Unknown plan_type")


if __name__ == "__main__":
    main()