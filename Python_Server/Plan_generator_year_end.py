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


# ===================================================================
# 1. Common Helper Functions
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
    """Writes the XML tree to a file with proper indentation."""
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir): os.makedirs(output_dir)
    if sys.version_info.major == 3 and sys.version_info.minor >= 9:
        ET.indent(tree, space="  ", level=0)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)


# ===================================================================
# 2. Logic for "With Route" Mode
# ===================================================================

GRAPH_REGISTRY = {}


def register_graph(graph):
    """Registers a graph object for use in cached functions."""
    graph_id = id(graph)
    if graph_id not in GRAPH_REGISTRY:
        GRAPH_REGISTRY[graph_id] = graph
    return graph_id


@lru_cache(maxsize=100000)
def find_nearest_node_cached(graph_id, lon, lat):
    """(Cached) Finds the nearest node in the graph."""
    graph = GRAPH_REGISTRY.get(graph_id)
    if graph is None: return None
    return ox.distance.nearest_nodes(graph, X=round(lon, 6), Y=round(lat, 6))


@lru_cache(maxsize=100000)
def get_shortest_path_cached(graph_id, orig_node, dest_node, weight):
    """(Cached) Gets the list of nodes for the shortest path."""
    graph = GRAPH_REGISTRY.get(graph_id)
    if graph is None: return []
    try:
        return nx.shortest_path(graph, orig_node, dest_node, weight=weight)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []


@lru_cache(maxsize=100000)
def get_shortest_path_length_cached(graph_id, orig_node, dest_node, weight):
    """(Cached) Gets the length of the shortest path."""
    graph = GRAPH_REGISTRY.get(graph_id)
    if graph is None: return 0.0
    try:
        return nx.shortest_path_length(graph, orig_node, dest_node, weight=weight)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return 0.0


def load_data(data_folder):
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


def find_nearest_station_optimized(xy, station_data):
    """Efficiently finds the nearest station using KDTree."""
    kdtree = station_data['kdtree']
    _, idx = kdtree.query(xy)
    return station_data['gdf'].index[idx]


def get_spatial_route(graph, origin_xy, destination_xy):
    """Gets the route and distance for spatial networks (e.g., walk, drive)."""
    try:
        graph_id = id(graph)
        orig_node = find_nearest_node_cached(graph_id, origin_xy[0], origin_xy[1])
        dest_node = find_nearest_node_cached(graph_id, destination_xy[0], destination_xy[1])
        if orig_node is None or dest_node is None or orig_node == dest_node: return [], 0.0
        path = get_shortest_path_cached(graph_id, orig_node, dest_node, weight='length')
        distance = get_shortest_path_length_cached(graph_id, orig_node, dest_node, weight='length')
        return path, distance
    except Exception as e:
        sys.stderr.write(f"[Spatial Routing Error] {e}\n")
        return [], 0.0


def get_station_route(graph, station_data, origin_xy, destination_xy):
    """Gets the route and distance for station-based networks (e.g., bus, subway)."""
    try:
        orig_station = find_nearest_station_optimized(origin_xy, station_data)
        dest_station = find_nearest_station_optimized(destination_xy, station_data)
        if orig_station not in graph or dest_station not in graph: return [], 0.0
        graph_id = id(graph)
        path = get_shortest_path_cached(graph_id, orig_station, dest_station, weight='weight')
        distance = get_shortest_path_length_cached(graph_id, orig_station, dest_station, weight='weight')
        return path, distance
    except Exception as e:
        sys.stderr.write(f"[Station Routing Error] {e}\n")
        return [], 0.0


def get_route(mode, start_xy, end_xy, graphs, stations):
    """Selects the appropriate routing function based on the travel mode."""
    mode = mode.lower()
    graph = graphs.get(mode)
    if not graph: return [], 0.0
    if mode in ['bus', 'subway']:
        station_data = stations.get(mode)
        return get_station_route(graph, station_data, start_xy, end_xy) if station_data else ([], 0.0)
    else:
        return get_spatial_route(graph, start_xy, end_xy)


def build_single_plan_element_with_route(person_id, plan_list, plan_type, graphs, stations, speeds_kmh):
    """Builds a plan element for a single person, including a detailed route."""
    plan = ET.Element("plan", type=plan_type)
    current_time_sec = 0
    base_graph = graphs.get('walk')
    for i, (act_type, facilityID, lon, lat, duration, mode) in enumerate(plan_list):
        activity_link = ""
        if base_graph:
            try:
                graph_id = id(base_graph)
                node = find_nearest_node_cached(graph_id, lon, lat)
                activity_link = str(node) if node else ""
            except Exception as e:
                sys.stderr.write(f"Could not find nearest node for Person {person_id}: {e}\n")
        ET.SubElement(plan, "activity", type=act_type, facilityID=facilityID, link=activity_link, x=str(lon),
                      y=str(lat), end_time=seconds_to_time_str(current_time_sec + duration))
        if i < len(plan_list) - 1:
            next_act = plan_list[i + 1]
            path, distance = get_route(mode, (lon, lat), (next_act[2], next_act[3]), graphs, stations)
            speed_kmh = speeds_kmh.get(mode.lower(), 5.0)
            travel_time = (distance / (speed_kmh / 3.6)) if speed_kmh > 0 else 0
            leg = ET.SubElement(plan, "leg", mode=mode, dep_time=seconds_to_time_str(current_time_sec + duration),
                                trav_time=seconds_to_time_str(round(travel_time)))
            if path:
                ET.SubElement(leg, "route", type="links",
                              distance=f"{distance / 1000.0:.4f}").text = f"[{', '.join(map(str, path))}]"
            current_time_sec += duration + round(travel_time)
    return plan


# ===================================================================
# 3. Logic for "Without Route" Mode
# ===================================================================

def build_single_plan_element_without_route(person_id, plan_list, plan_type, speeds_kmh, detour_factors):
    """
    without_route version: Does not require any pre-loaded data.
    Calculates distance and time from detour factors. The 'link' attribute will be empty.
    """
    plan = ET.Element("plan", type=plan_type)
    current_time_sec = 0
    for i, (act_type, facilityID, lon, lat, duration, mode) in enumerate(plan_list):
        # The 'link' attribute is left empty as no graph is loaded to find the nearest node.
        ET.SubElement(plan, "activity", type=act_type, facilityID=facilityID, link="", x=str(lon),
                      y=str(lat), end_time=seconds_to_time_str(current_time_sec + duration))
        if i < len(plan_list) - 1:
            next_act = plan_list[i + 1]
            next_lon, next_lat = next_act[2], next_act[3]
            # Calculation using straight-line distance and detour factor
            euclidean_distance = ox.distance.great_circle_vec(lat, lon, next_lat, next_lon)
            detour_factor = detour_factors.get(mode.lower(), 1.2)  # Default detour factor is 1.2
            travel_distance = euclidean_distance * detour_factor
            speed_kmh = speeds_kmh.get(mode.lower(), 5.0)
            travel_time = (travel_distance / (speed_kmh / 3.6)) if speed_kmh > 0 else 0
            # Create a <leg> without a <route> sub-element
            ET.SubElement(plan, "leg", mode=mode, dep_time=seconds_to_time_str(current_time_sec + duration),
                          trav_time=seconds_to_time_str(round(travel_time)))
            current_time_sec += duration + round(travel_time)
    return plan


# ===================================================================
# 4. Workflows for Multiprocessing
# ===================================================================

# --- Worker setup for "With Route" mode ---
WORKER_GRAPHS, WORKER_STATIONS, WORKER_SPEEDS_WITH_ROUTE = None, None, None


def init_worker_with_route(data_folder, speeds_kmh):
    """Initializes a worker process for the 'with route' mode."""
    global WORKER_GRAPHS, WORKER_STATIONS, WORKER_SPEEDS_WITH_ROUTE
    WORKER_GRAPHS, WORKER_STATIONS = load_data(data_folder)
    WORKER_SPEEDS_WITH_ROUTE = speeds_kmh
    for graph in WORKER_GRAPHS.values(): register_graph(graph)
    find_nearest_node_cached.cache_clear()
    get_shortest_path_cached.cache_clear()
    get_shortest_path_length_cached.cache_clear()


def process_single_row_full_with_route(row):
    """(Worker function) Generates a full plan with routes for a single row of data."""
    person_id = row['PID']
    new_person_element = ET.Element("person", ID=str(person_id))
    if (weekday_str := row.get('Weekday', '')) and (plan_list := parse_weekday_string(weekday_str)):
        new_person_element.append(
            build_single_plan_element_with_route(person_id, plan_list, "typical weekday", WORKER_GRAPHS,
                                                 WORKER_STATIONS, WORKER_SPEEDS_WITH_ROUTE))
    if (weekend_str := row.get('Weekend', '')) and (plan_list := parse_weekday_string(weekend_str)):
        new_person_element.append(
            build_single_plan_element_with_route(person_id, plan_list, "typical weekend", WORKER_GRAPHS,
                                                 WORKER_STATIONS, WORKER_SPEEDS_WITH_ROUTE))
    return ET.tostring(new_person_element, encoding='unicode') if len(list(new_person_element)) > 0 else None


# --- Worker setup for "Without Route" mode ---
WORKER_SPEEDS_WITHOUT_ROUTE, WORKER_DETOUR_FACTORS = None, None


def init_worker_without_route(speeds_kmh, detour_factors):
    """Initializes a worker process for the 'without route' mode."""
    global WORKER_SPEEDS_WITHOUT_ROUTE, WORKER_DETOUR_FACTORS
    WORKER_SPEEDS_WITHOUT_ROUTE = speeds_kmh
    WORKER_DETOUR_FACTORS = detour_factors


def process_single_row_full_without_route(row):
    """(Worker function) Generates a full plan without routes for a single row of data."""
    person_id = row['PID']
    new_person_element = ET.Element("person", ID=str(person_id))
    if (weekday_str := row.get('Weekday', '')) and (plan_list := parse_weekday_string(weekday_str)):
        new_person_element.append(build_single_plan_element_without_route(person_id, plan_list, "typical weekday",
                                                                          WORKER_SPEEDS_WITHOUT_ROUTE,
                                                                          WORKER_DETOUR_FACTORS))
    if (weekend_str := row.get('Weekend', '')) and (plan_list := parse_weekday_string(weekend_str)):
        new_person_element.append(build_single_plan_element_without_route(person_id, plan_list, "typical weekend",
                                                                          WORKER_SPEEDS_WITHOUT_ROUTE,
                                                                          WORKER_DETOUR_FACTORS))
    return ET.tostring(new_person_element, encoding='unicode') if len(list(new_person_element)) > 0 else None


# ===================================================================
# 5. Main Logic Functions
# ===================================================================

def _generate_year_end_plan_base(csv_path, xml_path, xml_second_path, process_func, desc, initializer, init_args):
    """Base function for processing year-end changes, applicable to both modes."""
    print(f"--- Starting Year-End Plan Processing ({desc}) ---")
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        print(f"Successfully loaded existing XML from: {xml_path}")
    except (FileNotFoundError, ET.ParseError):
        root = ET.Element("people")
        tree = ET.ElementTree(root)
        print(f"XML file not found at {xml_path}. A new one will be created.")

    try:
        with open(csv_path, mode='r', encoding='utf-8-sig') as infile:
            all_csv_rows = list(csv.DictReader(infile))
        print(f"Read {len(all_csv_rows)} rows from CSV: {csv_path}")
    except FileNotFoundError:
        sys.stderr.write(f"Error: CSV file not found at '{csv_path}'\n")
        return

    csv_pids = {row['PID'] for row in all_csv_rows}
    rows_to_update = [row for row in all_csv_rows if row.get('Change') == '1']
    pids_to_update = {row['PID'] for row in rows_to_update}

    print(f"Found {len(csv_pids)} unique PIDs in CSV.")
    print(f"Found {len(rows_to_update)} persons marked for regeneration (Change=1).")

    # Remove persons from XML who are not in the CSV
    persons_to_remove_sync = [p for p in root.findall('person') if p.get('ID') not in csv_pids]
    if persons_to_remove_sync:
        print(f"Syncing: Removing {len(persons_to_remove_sync)} persons from XML not in CSV...")
        for person in persons_to_remove_sync:
            root.remove(person)

    # Remove old plans for persons who need an update
    if pids_to_update:
        print(f"Regeneration: Removing {len(pids_to_update)} persons from XML for plan regeneration...")
        for pid in pids_to_update:
            if (existing_person := root.find(f".//person[@ID='{pid}']")) is not None:
                root.remove(existing_person)

    # Generate new plans using multiprocessing
    if rows_to_update:
        # Note: max_workers can be adjusted based on your machine's CPU cores
        with ProcessPoolExecutor(max_workers=4, initializer=initializer, initargs=init_args) as executor:
            results = list(tqdm(executor.map(process_func, rows_to_update), total=len(rows_to_update),
                                desc=f"Regenerating Plans ({desc})"))

        added_count = sum(1 for xml_string in results if xml_string and root.append(ET.fromstring(xml_string)))
        print(f"Regeneration: Successfully added {added_count} new plans to the XML tree.")

    # Save the final XML
    try:
        write_xml(tree, xml_path)
        print(f"Successfully saved updated XML to: {xml_path}")
        if os.path.dirname(xml_second_path): os.makedirs(os.path.dirname(xml_second_path), exist_ok=True)
        shutil.copy2(xml_path, xml_second_path)
        print(f"Successfully copied updated XML to: {xml_second_path}")
    except Exception as e:
        sys.stderr.write(f"Error saving or copying final XML file: {e}\n")

    print(f"--- Year-End Plan Processing Finished ({desc}) ---")


def generate_year_end_plan(csv_path, xml_path, xml_second_path, data_folder, speeds_kmh):
    """Processes year-end changes - with route version."""
    _generate_year_end_plan_base(csv_path, xml_path, xml_second_path,
                                 process_single_row_full_with_route,
                                 "With Route",
                                 init_worker_with_route,
                                 (data_folder, speeds_kmh))


def generate_year_end_plan_without_route(csv_path, xml_path, xml_second_path, speeds_kmh, detour_factors):
    """Processes year-end changes - without route version."""
    _generate_year_end_plan_base(csv_path, xml_path, xml_second_path,
                                 process_single_row_full_without_route,
                                 "Without Route",
                                 init_worker_without_route,
                                 (speeds_kmh, detour_factors))


if __name__ == '__main__':
    # --- Example of how to call the functions ---

    # Common parameters
    csv_input_path = "path/to/your/year_end_changes.csv"
    xml_output_path = "path/to/your/output_plan.xml"
    xml_backup_path = "path/to/your/backup/output_plan.xml"

    # Define speeds for various transport modes (km/h)
    SPEEDS_KMH = {
        'walk': 5, 'taxi': 40, 'bus': 25, 'subway': 50,
        'private_vehicle': 45, 'two_wheels': 15, 'for-hire_vehicle': 40
    }

    # ---- Option 1: Call the "With Route" version ----
    # Requires the path to the network data folder
    # network_data_folder = "path/to/your/network_data"
    # generate_year_end_plan(
    #     csv_path=csv_input_path,
    #     xml_path=xml_output_path,
    #     xml_second_path=xml_backup_path,
    #     data_folder=network_data_folder,
    #     speeds_kmh=SPEEDS_KMH
    # )

    # ---- Option 2: Call the "Without Route" version ----
    # Requires defining the detour factors for various transport modes
    DETOUR_FACTORS = {
        'walk': 1.2, 'taxi': 1.4, 'bus': 1.8, 'subway': 1.6,
        'private_vehicle': 1.4, 'two_wheels': 1.3, 'for-hire_vehicle': 1.4
    }
    # generate_year_end_plan_without_route(
    #     csv_path=csv_input_path,
    #     xml_path=xml_output_path,
    #     xml_second_path=xml_backup_path,
    #     speeds_kmh=SPEEDS_KMH,
    #     detour_factors=DETOUR_FACTORS
    # )

    print("Example calls are commented out. Please edit the paths and uncomment the desired function to run.")

