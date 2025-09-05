#Parts of the code in this model were generated with the assistance of AI and subsequently revised and validated by the author.

import xml.etree.ElementTree as ET
from datetime import timedelta
import networkx as nx
import osmnx as ox
import pickle
import os
import csv
import re
import sys
import shutil
from tqdm import tqdm
from functools import lru_cache
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from scipy.spatial import KDTree

def _PG_CANONICAL_MODE(mode):
    m = str(mode).strip().lower().replace('-', '_')
    if m in ('two_wheel','two_wheels','bicycle','bike','motorcycle','scooter'): return 'Two_wheels'
    if m in ('walk','walking'): return 'Walk'
    if m in ('private_vehicle','car','auto','pv'): return 'Private_vehicle'
    if m in ('taxi','cab'): return 'Taxi'
    if m in ('for_hire_vehicle','for-hire_vehicle','fhv','ride_hail','rideshare','uber','lyft','other'): return 'For-hire_vehicle'
    if m in ('subway','metro'): return 'Subway'
    if m in ('bus',): return 'Bus'
    return mode


# ===================================================================
# 1. Helper Functions (Common)
# ===================================================================
def parse_weekday_string(weekday_str):
    """Parses a complex plan string into a list of activity tuples."""
    if not weekday_str or not isinstance(weekday_str, str): return []
    activity_content_list = re.findall(r'\[([^\[\]]+)\]', weekday_str)
    if not activity_content_list: return []
    plan_list = []
    pattern = re.compile(r"(\w+)\s*\((.*?)\)\s*(.*)")
    for act_str in activity_content_list:
        try:
            match = pattern.match(act_str.strip())
            if not match: continue
            act_type, facility_id, rest_of_string = match.groups()
            parts = rest_of_string.strip().split()
            if len(parts) < 2: continue
            lon, lat = float(parts[0]), float(parts[1])
            duration = int(parts[2]) if len(parts) >= 3 else 0
            mode = parts[3] if len(parts) >= 4 else ""
            plan_list.append((act_type, facility_id, lon, lat, duration, mode))
        except (ValueError, IndexError):
            continue
    return plan_list


def seconds_to_time_str(seconds):
    """Converts seconds to a 'HH:MM:SS' formatted string."""
    return str(timedelta(seconds=int(seconds)))


def write_xml(tree, output_file):
    """Writes the XML tree to a file with proper indentation.
    Ensures <route .../> becomes <route ...> </route> to match downstream parser expectations.
    """
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir): os.makedirs(output_dir)
    if sys.version_info.major == 3 and sys.version_info.minor >= 9:
        ET.indent(tree, space="  ", level=0)
    tmp_path = output_file + ".tmp"
    tree.write(tmp_path, encoding='utf-8', xml_declaration=True)
    with open(tmp_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = re.sub(r'<route([^>]*)/>', r'<route\1> </route>', content)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    try:
        os.remove(tmp_path)
    except Exception:
        pass


# ===================================================================
# 2. Logic for "With Route" Mode (Requires Data Loading)
# ===================================================================

GRAPH_REGISTRY = {}


def register_graph(graph):
    graph_id = id(graph)
    if graph_id not in GRAPH_REGISTRY:
        GRAPH_REGISTRY[graph_id] = graph
    return graph_id


@lru_cache(maxsize=100000)
def find_nearest_node_cached(graph_id, lon, lat):
    graph = GRAPH_REGISTRY.get(graph_id)
    if graph is None: return None
    return ox.distance.nearest_nodes(graph, X=round(lon, 6), Y=round(lat, 6))


# ... (Other cached functions for routing remain here) ...
@lru_cache(maxsize=100000)
def get_shortest_path_cached(graph_id, orig_node, dest_node, weight):
    graph = GRAPH_REGISTRY.get(graph_id)
    if graph is None: return []
    try:
        return nx.shortest_path(graph, orig_node, dest_node, weight=weight)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []


@lru_cache(maxsize=100000)
def get_shortest_path_length_cached(graph_id, orig_node, dest_node, weight):
    graph = GRAPH_REGISTRY.get(graph_id)
    if graph is None: return 0.0
    try:
        return nx.shortest_path_length(graph, orig_node, dest_node, weight=weight)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return 0.0


def load_data(data_folder):
    # ... (This function remains unchanged)
    """Loads network data, prioritizing disk cache."""
    graph_paths = {"walk": os.path.join(data_folder, "walk.graphml"), "taxi": os.path.join(data_folder, "taxi.graphml"),
                   "bus": os.path.join(data_folder, "bus.pkl"), "subway": os.path.join(data_folder, "subway.pkl"),
                   "private_vehicle": os.path.join(data_folder, "taxi.graphml"),
                   "two_wheels": os.path.join(data_folder, "walk.graphml"),
                   "for-hire_vehicle": os.path.join(data_folder, "taxi.graphml")}
    station_paths = {"bus": os.path.join(data_folder, "bus_station.pkl"),
                     "subway": os.path.join(data_folder, "subway_station.pkl")}
    graphs, stations = {}, {}
    cache_folder = os.path.join(data_folder, "precomputed_cache")
    os.makedirs(cache_folder, exist_ok=True)
    for mode, path in graph_paths.items():
        if os.path.exists(path):
            cache_path = os.path.join(cache_folder, f"{mode}_graph.pkl")
            if os.path.exists(cache_path):
                with open(cache_path, "rb") as f:
                    graph = pickle.load(f)
            else:
                if path.endswith(".graphml"):
                    graph = ox.load_graphml(path)
                else:
                    with open(path, "rb") as f:
                        graph = pickle.load(f)
                with open(cache_path, "wb") as f:
                    pickle.dump(graph, f)
            graphs[mode.lower()] = graph
            register_graph(graph)

    for mode, path in station_paths.items():
        if os.path.exists(path):
            with open(path, "rb") as f:
                gdf = pickle.load(f)
                if not gdf.empty:
                    coordinates = np.array(list(zip(gdf.geometry.x, gdf.geometry.y)))
                    kdtree = KDTree(coordinates)
                    stations[mode.lower()] = {"gdf": gdf, "kdtree": kdtree}
    return graphs, stations


# ... (All other functions for the "with route" mode remain unchanged) ...
def find_nearest_station_optimized(xy, station_data):
    """Efficiently finds the nearest station using KDTree."""
    gdf = station_data['gdf']
    kdtree = station_data['kdtree']
    distance, idx = kdtree.query(xy)
    return gdf.index[idx]


def get_spatial_route(graph, origin_xy, destination_xy):
    try:
        graph_id = id(graph)
        orig_node = find_nearest_node_cached(graph_id, origin_xy[0], origin_xy[1])
        dest_node = find_nearest_node_cached(graph_id, destination_xy[0], destination_xy[1])
        if orig_node is None or dest_node is None or orig_node == dest_node:
            return [], 0.0
        path = get_shortest_path_cached(graph_id, orig_node, dest_node, weight='length')
        distance = get_shortest_path_length_cached(graph_id, orig_node, dest_node, weight='length')
        return path, distance
    except Exception as e:
        sys.stderr.write(f"[Spatial Routing Error] {e}\n")
        return [], 0.0


def get_station_route(graph, station_data, origin_xy, destination_xy):
    try:
        orig_station = find_nearest_station_optimized(origin_xy, station_data)
        dest_station = find_nearest_station_optimized(destination_xy, station_data)
        if not orig_station or not dest_station or orig_station not in graph or dest_station not in graph:
            raise ValueError("Station not found or not in graph.")
        graph_id = id(graph)
        path = get_shortest_path_cached(graph_id, orig_station, dest_station, weight='weight')
        distance = get_shortest_path_length_cached(graph_id, orig_station, dest_station, weight='weight')
        return path, distance
    except Exception as e:
        sys.stderr.write(f"[Station Routing Error] {e}\n")
        return [], 0.0


def get_route(mode, start_xy, end_xy, graphs, stations):
    mode = mode.lower()
    graph = graphs.get(mode)
    if not graph: return [], 0.0
    if mode in ['bus', 'subway']:
        station_data = stations.get(mode)
        if not station_data: return [], 0.0
        return get_station_route(graph, station_data, start_xy, end_xy)
    else:
        return get_spatial_route(graph, start_xy, end_xy)


def build_single_plan_element_with_route(person_id, plan_list, plan_type, graphs, stations, speeds_kmh):
    plan = ET.Element("plan", type=plan_type)
    current_time_sec = 0
    base_graph = graphs.get('walk')
    for i in range(len(plan_list)):
        act_type, facilityID, lon, lat, duration, mode = plan_list[i]
        activity_link = ""
        if base_graph:
            try:
                graph_id = id(base_graph)
                node = find_nearest_node_cached(graph_id, lon, lat)
                activity_link = str(node) if node else ""
            except Exception as e:
                sys.stderr.write(f"Could not find nearest node for Person {person_id}: {e}\n")
        ET.SubElement(plan, "activity", type=act_type, facilityID=facilityID, x=str(lon), y=str(lat), end_time=seconds_to_time_str(current_time_sec + duration))
        if i < len(plan_list) - 1:
            next_act = plan_list[i + 1]
            next_lon, next_lat = next_act[2], next_act[3]
            path, distance = get_route(mode, (lon, lat), (next_lon, next_lat), graphs, stations)
            speed_kmh = speeds_kmh.get(mode.lower(), 5.0)
            travel_time = distance / (speed_kmh / 3.6) if speed_kmh > 0 else 0
            leg = ET.SubElement(plan, "leg", mode=_PG_CANONICAL_MODE(mode), dep_time=seconds_to_time_str(current_time_sec + duration),
                                trav_time=seconds_to_time_str(round(travel_time)))
            if path:
                distance_km = distance / 1000.0
                route_text = f"[{', '.join(map(str, path))}]"
                rt = ET.SubElement(leg, "route", distance=f"{distance_km:.6f}", travel_time=seconds_to_time_str(round(travel_time)))
                rt.text = " "
            current_time_sec += duration + round(travel_time)
        else:
            current_time_sec += duration
    return plan


# ===================================================================
# 3. Logic for "Without Route" without_route Mode
# ===================================================================

def build_single_plan_element_without_route(person_id, plan_list, plan_type, speeds_kmh, detour_factors):
    """
    without_route version: Does not require any pre-loaded data.
    Calculates distance and time from detour factors. The 'link' attribute will be empty.
    """
    plan = ET.Element("plan", type=plan_type)
    current_time_sec = 0
    for i in range(len(plan_list)):
        act_type, facilityID, lon, lat, duration, mode = plan_list[i]
        # The 'link' attribute is left empty as no graph is loaded to find the nearest node.
        ET.SubElement(plan, "activity", type=act_type, facilityID=facilityID, x=str(lon), y=str(lat), end_time=seconds_to_time_str(current_time_sec + duration))
        if i < len(plan_list) - 1:
            next_act = plan_list[i + 1]
            next_lon, next_lat = next_act[2], next_act[3]
            euclidean_distance = ox.distance.great_circle_vec(lat, lon, next_lat, next_lon)
            detour_factor = detour_factors.get(mode.lower(), 1.0)
            travel_distance = euclidean_distance * detour_factor
            speed_kmh = speeds_kmh.get(mode.lower(), 5.0)
            travel_time = travel_distance / (speed_kmh / 3.6) if speed_kmh > 0 else 0
            ET.SubElement(plan, "leg", mode=mode, dep_time=seconds_to_time_str(current_time_sec + duration),
                          trav_time=seconds_to_time_str(round(travel_time)))
            current_time_sec += duration + round(travel_time)
        else:
            current_time_sec += duration
    return plan


# ===================================================================
# 4. Multiprocessing Workflows (for both modes)
# ===================================================================

# --- Worker setup for "With Route" mode ---
WORKER_GRAPHS, WORKER_STATIONS, WORKER_SPEEDS_WITH_ROUTE, WORKER_DETOUR_FACTORS = None, None, None, None


def init_worker_with_route(data_folder, speeds_kmh):
    global WORKER_GRAPHS, WORKER_STATIONS, WORKER_SPEEDS_WITH_ROUTE
    WORKER_GRAPHS, WORKER_STATIONS = load_data(data_folder)
    WORKER_SPEEDS_WITH_ROUTE = speeds_kmh
    for graph in WORKER_GRAPHS.values():
        register_graph(graph)
    find_nearest_node_cached.cache_clear()
    get_shortest_path_cached.cache_clear()
    get_shortest_path_length_cached.cache_clear()


# --- 【新】Worker setup for "without_route" mode ---
WORKER_SPEEDS_without_route, WORKER_DETOUR_FACTORS_without_route = None, None


def init_worker_without_route(speeds_kmh, detour_factors):
    global WORKER_SPEEDS_without_route, WORKER_DETOUR_FACTORS_without_route
    WORKER_SPEEDS_without_route = speeds_kmh
    WORKER_DETOUR_FACTORS_without_route = detour_factors


# --- Wrapper functions for ProcessPoolExecutor ---

def process_single_row_full_with_route(row):
    person_id = row['PID']
    new_person_element = ET.Element("person", ID=str(person_id))
    if (weekday_str := row.get('Weekday', '')) and (plan_list := parse_weekday_string(weekday_str)):
        weekday_plan = build_single_plan_element_with_route(person_id, plan_list, "typical weekday", WORKER_GRAPHS,
                                                            WORKER_STATIONS, WORKER_SPEEDS_WITH_ROUTE)
        new_person_element.append(weekday_plan)
    if 'Weekend' in row and (weekend_str := row.get('Weekend', '')) and (
    plan_list := parse_weekday_string(weekend_str)):
        weekend_plan = build_single_plan_element_with_route(person_id, plan_list, "typical weekend", WORKER_GRAPHS,
                                                            WORKER_STATIONS, WORKER_SPEEDS_WITH_ROUTE)
        new_person_element.append(weekend_plan)
    return ET.tostring(new_person_element, encoding='unicode') if len(list(new_person_element)) > 0 else None


def process_single_row_weekday_with_route(row):
    person_id = row['PID']
    if (weekday_str := row.get('Weekday', '')) and (plan_list := parse_weekday_string(weekday_str)):
        weekday_plan = build_single_plan_element_with_route(person_id, plan_list, "typical weekday", WORKER_GRAPHS,
                                                            WORKER_STATIONS, WORKER_SPEEDS_WITH_ROUTE)
        return (person_id, ET.tostring(weekday_plan, encoding='unicode'))
    return None


def process_single_row_full_without_route(row):
    person_id = row['PID']
    new_person_element = ET.Element("person", ID=str(person_id))
    if (weekday_str := row.get('Weekday', '')) and (plan_list := parse_weekday_string(weekday_str)):
        weekday_plan = build_single_plan_element_without_route(person_id, plan_list, "typical weekday",
                                                            WORKER_SPEEDS_without_route, WORKER_DETOUR_FACTORS_without_route)
        new_person_element.append(weekday_plan)
    if 'Weekend' in row and (weekend_str := row.get('Weekend', '')) and (
    plan_list := parse_weekday_string(weekend_str)):
        weekend_plan = build_single_plan_element_without_route(person_id, plan_list, "typical weekend",
                                                            WORKER_SPEEDS_without_route, WORKER_DETOUR_FACTORS_without_route)
        new_person_element.append(weekend_plan)
    return ET.tostring(new_person_element, encoding='unicode') if len(list(new_person_element)) > 0 else None


def process_single_row_weekday_without_route(row):
    person_id = row['PID']
    if (weekday_str := row.get('Weekday', '')) and (plan_list := parse_weekday_string(weekday_str)):
        weekday_plan = build_single_plan_element_without_route(person_id, plan_list, "typical weekday",
                                                            WORKER_SPEEDS_without_route, WORKER_DETOUR_FACTORS_without_route)
        return (person_id, ET.tostring(weekday_plan, encoding='unicode'))
    return None


# --- Main Entry Points ---

def _generate_plan_base(csv_input_file, output_xml_file, second_output_path, process_func, desc, initializer,
                        init_args):
    try:
        tree = ET.parse(output_xml_file)
        root = tree.getroot()
    except (FileNotFoundError, ET.ParseError):
        root = ET.Element("population")
        tree = ET.ElementTree(root)
    with open(csv_input_file, mode='r', encoding='utf-8-sig') as infile:
        rows_to_process = list(csv.DictReader(infile))

    try:
        with ProcessPoolExecutor(max_workers=1, initializer=initializer, initargs=init_args) as executor:
            results = list(tqdm(executor.map(process_func, rows_to_process), total=len(rows_to_process), desc=desc))
    except Exception as e:
        print('[Fallback] Process pool failed:', e)
        results = []
        for row in tqdm(rows_to_process, desc=desc + ' (sequential)'):
            try:
                out = process_func(row)
            except Exception as inner_e:
                out = None
                print('[Row error]', row.get('PID'), inner_e)
            if out is not None:
                results.append(out)

    return tree, root, results


# --- Entry points for "With Route" mode ---
def generate_full_plan(csv_input_file, output_xml_file, second_output_path, speeds_kmh, data_folder):
    tree, root, results = _generate_plan_base(csv_input_file, output_xml_file, second_output_path,
                                              process_single_row_full_with_route, "Generating Full Plans (with route)",
                                              init_worker_with_route, (data_folder, speeds_kmh))
    pids_to_update = {row['PID'] for row in csv.DictReader(open(csv_input_file, mode='r', encoding='utf-8-sig'))}
    for person_id in pids_to_update:
        if (existing_person := root.find(f".//person[@ID='{person_id}']")) is not None:
            root.remove(existing_person)
    for xml_string in filter(None, results):
        root.append(ET.fromstring(xml_string))
    write_xml(tree, output_xml_file)
    shutil.copy2(output_xml_file, second_output_path)
    print(f"Successfully generated full plans WITH routes in {output_xml_file}")


def generate_weekday_plan_only(csv_input_file, output_xml_file, second_output_path, speeds_kmh, data_folder):
    tree, root, results = _generate_plan_base(csv_input_file, output_xml_file, second_output_path,
                                              process_single_row_weekday_with_route,
                                              "Updating Weekday Plans (with route)", init_worker_with_route,
                                              (data_folder, speeds_kmh))
    for person_id, plan_xml_string in filter(None, results):
        person_element = root.find(f".//person[@ID='{person_id}']") or ET.SubElement(root, "person", ID=str(person_id))
        if (old_plan := person_element.find("./plan[@type='typical weekday']")) is not None:
            person_element.remove(old_plan)
        person_element.append(ET.fromstring(plan_xml_string))
    write_xml(tree, output_xml_file)
    shutil.copy2(output_xml_file, second_output_path)
    print(f"Successfully updated weekday plans WITH routes in {output_xml_file}")


# --- Entry points for "without_route" mode ---
def generate_full_plan_without_route(csv_input_file, output_xml_file, second_output_path, speeds_kmh, detour_factors):
    tree, root, results = _generate_plan_base(csv_input_file, output_xml_file, second_output_path,
                                              process_single_row_full_without_route, "Generating Full Plans (no route)",
                                              init_worker_without_route, (speeds_kmh, detour_factors))
    pids_to_update = {row['PID'] for row in csv.DictReader(open(csv_input_file, mode='r', encoding='utf-8-sig'))}
    for person_id in pids_to_update:
        if (existing_person := root.find(f".//person[@ID='{person_id}']")) is not None:
            root.remove(existing_person)
    for xml_string in filter(None, results):
        root.append(ET.fromstring(xml_string))
    write_xml(tree, output_xml_file)
    shutil.copy2(output_xml_file, second_output_path)
    print(f"Successfully generated full plans WITHOUT routes in {output_xml_file}")


def generate_weekday_plan_only_without_route(csv_input_file, output_xml_file, second_output_path, speeds_kmh,
                                          detour_factors):
    tree, root, results = _generate_plan_base(csv_input_file, output_xml_file, second_output_path,
                                              process_single_row_weekday_without_route,
                                              "Updating Weekday Plans (no route)", init_worker_without_route,
                                              (speeds_kmh, detour_factors))
    for person_id, plan_xml_string in filter(None, results):
        person_element = root.find(f".//person[@ID='{person_id}']") or ET.SubElement(root, "person", ID=str(person_id))
        if (old_plan := person_element.find("./plan[@type='typical weekday']")) is not None:
            person_element.remove(old_plan)
        person_element.append(ET.fromstring(plan_xml_string))
    write_xml(tree, output_xml_file)
    shutil.copy2(output_xml_file, second_output_path)
    print(f"Successfully updated weekday plans WITHOUT routes in {output_xml_file}")
