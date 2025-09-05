#Parts of the code in this model were generated with the assistance of AI and subsequently revised and validated by the author.
import xml.etree.ElementTree as ET
from collections import Counter
import ast
import numpy as np
import osmnx as ox
import contextlib
from concurrent.futures import ThreadPoolExecutor
from hispot.FIFLP import MaFM
import pandas as pd


def normalize_edge(edge):
    """
    Normalize edges so that the smaller node always comes first.
    """
    u, v, k = edge
    return (min(u, v), max(u, v), k)


def parse_route(route):
    """
    Parse a single route element and extract edge information.
    """
    return ast.literal_eval(route.text.strip())


def parse_routes_from_xml(xml_path, target_ids):
    """
    Parse the XML file to extract routes for target people based on person IDs.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    target_people = []
    routes = []
    for person in root.findall('.//person'):
        if person.get('ID') in target_ids:
            target_people.append(person)
            routes.extend(person.findall(".//leg/route"))

    # Parallel route parsing
    with ThreadPoolExecutor() as executor:
        return list(executor.map(parse_route, routes)), target_people


def count_edges(routes):
    """
    Count the frequency of each edge in the routes.
    """
    edge_counter = Counter()
    for edges in routes:
        normalized_edges = [normalize_edge(edge) for edge in edges]
        edge_counter.update(normalized_edges)
    return edge_counter


def create_node_index(Vp_np):
    """
    Create a mapping from nodes to indices.
    """
    nodes = list(set(node for edge in Vp_np for node in edge))
    node_index = {node: idx for idx, node in enumerate(nodes)}
    return nodes, node_index


def get_facilities_coordinates(graph, nodes, selected_vector):
    """
    Get the latitude and longitude coordinates of selected facilities.
    """
    return np.array([(graph.nodes[nodes[i]]['x'], graph.nodes[nodes[i]]['y']) for i in selected_vector])


def load_target_ids_from_csv(csv_path):
    """
    Load target user IDs from a CSV file. The file should only have one column 'PID'.
    """
    target_ids_df = pd.read_csv(csv_path)
    return target_ids_df['PID'].astype(str).tolist()


def flow_capturing(number_facility, target_ids, road_network_path, xml_path, start_tfid):
    """
    Main flow capturing function to perform facility location selection.
    """
    # Load road network graph
    graph = ox.load_graphml(filepath=road_network_path).to_undirected()

    if graph is None:
        print("No graph found.")

    # Parse routes from XML for given target people
    routes, target_people = parse_routes_from_xml(xml_path, target_ids)

    # Count edges in the routes
    edge_counter = count_edges(routes)

    # Prepare data for facility location problem
    Vp = [list(edge[:2]) for edge in edge_counter]
    Fp = list(edge_counter.values())

    Vp_np = np.array(Vp)
    Fp_np = np.array(Fp)

    num_path = len(edge_counter)  # Number of paths

    # Create node index
    nodes, node_index = create_node_index(Vp_np)

    # Map edges to node indices
    rVp_np = [[node_index[edge[0]], node_index[edge[1]]] for edge in Vp_np]
    num_point = len(nodes)  # Number of nodes

    # Disable print output during solving
    with open(os.devnull, 'w') as f, contextlib.redirect_stdout(f):
        selected_path, selected_vector = MaFM(
            num_path=num_path,
            num_vector=num_point,
            path_vector=rVp_np,
            path_flow=Fp_np,
            num_choice=number_facility,  # Number of facilities to choose
            solver=PULP_CBC_CMD(),
        ).prob_solve()

    # Get the coordinates of selected facilities
    facilities_lon_lat = get_facilities_coordinates(graph, nodes, selected_vector)
    return facilities_lon_lat.tolist(), selected_path, selected_vector, nodes, rVp_np, target_people


def check_route_for_node(route_text, target_node):
    """
    Check if a specific node is in the route.
    """
    route_points = route_text.strip('[]').split('), (')
    route_points = ['(' + point.strip('()') + ')' for point in route_points]

    if target_node in route_points:
        return True

    node_parts = target_node.strip('()').split(',')
    reverse_node = f"({node_parts[1]}, {node_parts[0]}, {node_parts[2]})"
    if reverse_node in route_points:
        return True

    return False


def find_persons_with_nodes(selected_vector, selected_paths, target_people, nodes, rVp_np):
    """
    Find the persons whose paths pass through the selected facilities' nodes.
    """
    target_paths = [f"({nodes[rVp_np[path][0]]},{nodes[rVp_np[path][1]]},0)" for path in selected_paths]

    persons_with_target_nodes = {path: [] for path in target_paths}

    def process_person(person):
        routes = person.findall(".//leg/route")

        for route in routes:
            route_text = route.text
            for path in target_paths:
                if check_route_for_node(route_text, path):
                    person_id = person.get('ID')
                    persons_with_target_nodes[path].append(int(person_id))

    with ThreadPoolExecutor() as executor:
        executor.map(process_person, target_people)

    station_people = {sv_one: [] for sv_one in selected_vector}
    for sv_one in selected_vector:
        node_str = str(nodes[sv_one])
        for path, people in persons_with_target_nodes.items():
            if node_str in path:
                station_people[sv_one].extend(people)

    for key in station_people:
        station_people[key] = list(set(station_people[key]))

    return station_people


def save_facilities_to_csv(facilities_lon_lat, selected_vector, output_path):
    """
    Save the selected facilities to a CSV file.
    """
    facilities_df = pd.DataFrame(facilities_lon_lat, columns=['Longitude', 'Latitude'])
    facilities_df['TFID'] = [start_tfid + i for i in range(len(facilities_lon_lat))]
    facilities_df['Facility ID'] = selected_vector
    facilities_df.to_csv(output_path, index=False)


def save_assignments_to_csv(station_people, nodes, output_path):
    """
    Save the assignments of users to facilities in a CSV file.
    """
    assignment_data = []
    for facility_id, people in station_people.items():
        for person_id in people:
            assignment_data.append({'Facility ID': facility_id, 'Person ID': person_id})

    assignment_df = pd.DataFrame(assignment_data)
    assignment_df.to_csv(output_path, index=False)


def main():
    # Get the input parameters (for demonstration purposes, hardcoded here)
    xml_path = 'path_to_xml.xml'  # XML file path
    road_network_path = 'path_to_road_network.graphml'  # Road network file path
    target_ids_csv = 'target_ids.csv'  # CSV file containing user IDs
    number_facility = 3  # Number of facilities to build
    start_tfid = 1000  # Start TFID from this number
    facilities_output_path = 'facilities.csv'  # Output facilities file path
    assignments_output_path = 'assignments.csv'  # Output assignments file path

    # Load target user IDs from the CSV file
    target_ids = load_target_ids_from_csv(target_ids_csv)

    # Run flow capturing function
    facilities_lon_lat, selected_path, selected_vector, nodes, rVp_np, target_people = flow_capturing(
        number_facility, target_ids, road_network_path, xml_path, start_tfid)

    # Save the selected facilities to CSV
    save_facilities_to_csv(facilities_lon_lat, selected_vector, facilities_output_path)

    # Find and save the assignment of people to facilities
    station_people = find_persons_with_nodes(selected_vector, selected_path, target_people, nodes, rVp_np)
    save_assignments_to_csv(station_people, nodes, assignments_output_path)

    print("Facility and assignment data have been saved successfully.")


if __name__ == "__main__":
    main()
