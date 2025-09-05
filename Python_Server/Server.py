#Parts of the code in this model were generated with the assistance of AI and subsequently revised and validated by the author.

from flask import Flask, request, jsonify
import traceback

# Import functions from the original plan generator
from Plan_generator import (
    load_data,
    generate_full_plan,
    generate_weekday_plan_only,
    generate_full_plan_without_route,
    generate_weekday_plan_only_without_route
)
# Import function for deleting persons
from Plan_deleter import remove_persons_from_xml
# Import the new year-end processing functions
from Plan_generator_year_end import (
    generate_year_end_plan,
    generate_year_end_plan_without_route
)

app = Flask(__name__)

# --- Global Variables ---
# These are used by the "with route" modes
GRAPHS, STATIONS = None, None
ROUTE_DATA_FOLDER = None


# --- Helper Functions for Parsing ---
def _parse_speeds(form_data):
    """Parses speed parameters from form data."""
    speeds_str = form_data.get('speeds')
    if not speeds_str:
        raise ValueError("Missing 'speeds' parameter.")
    cleaned_speeds_str = speeds_str.strip('[] ').strip()
    speed_values = cleaned_speeds_str.split()
    mode_order = ["taxi", "subway", "walk", "private_vehicle", "bus", "two_wheels", "for-hire_vehicle"]
    return {mode: float(s) for mode, s in zip(mode_order, speed_values)}


def _parse_detour_factors(form_data):
    """Parses detour factor parameters from form data."""
    detour_factors_str = form_data.get('detour_factors')
    if not detour_factors_str:
        raise ValueError("Missing 'detour_factors' parameter.")
    cleaned_detour_str = detour_factors_str.strip('[] ').strip()
    detour_values = [float(x) for x in cleaned_detour_str.split()]
    mode_order = ['private_vehicle', 'two_wheels', 'walk', 'taxi', 'for-hire_vehicle', 'subway', 'bus']
    return dict(zip(mode_order, detour_values))


# ===================================================================
# API Routes
# ===================================================================

@app.route('/load_network_data', methods=['POST'])
def handle_data_loading():
    """Route 1: Load network data (for 'with route' modes)."""
    global GRAPHS, STATIONS, ROUTE_DATA_FOLDER
    print("\n--- Received request to load network data... ---")
    try:
        route_folder_path = request.form.get('route_folder')
        if not route_folder_path:
            return jsonify({"status": "error", "message": "Missing 'route_folder' parameter."}), 400
        ROUTE_DATA_FOLDER = route_folder_path
        graphs_loaded, stations_loaded = load_data(route_folder_path)
        if not graphs_loaded:
            return jsonify({"status": "error", "message": f"No graph data found in folder: {route_folder_path}"})
        GRAPHS, STATIONS = graphs_loaded, stations_loaded
        print("✅ Network data loaded into memory successfully by main process.")
        return jsonify({"status": "success", "message": "Network data has been successfully loaded."})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"A critical server error occurred: {str(e)}"}), 500


@app.route('/generate_full_plan', methods=['POST'])
def handle_full_plan_generation():
    """Route 2: Generate full plan (with route). Requires /load_network_data first."""
    if GRAPHS is None: return jsonify(
        {"status": "error", "message": "Server not ready; call /load_network_data first."}), 503
    print("\n--- Received request for /generate_full_plan (with route) ---")
    try:
        form_data = request.form
        csv_file, xml_file, second_path = (form_data.get(k) for k in ['csv_file', 'xml_file', 'second_path'])
        if not all([csv_file, xml_file, second_path]): return jsonify(
            {"status": "error", "message": "Missing file path parameters."}), 400

        speeds_kmh = _parse_speeds(form_data)
        generate_full_plan(csv_file, xml_file, second_path, speeds_kmh, ROUTE_DATA_FOLDER)
        print("✅ Full plan generation (with route) finished successfully.")
        return jsonify({"status": "success", "message": "Full plan generation task completed."})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"An exception occurred: {str(e)}"}), 500


@app.route('/generate_weekday_plan', methods=['POST'])
def handle_weekday_plan_update():
    """Route 3: Update weekday plan only (with route). Requires /load_network_data first."""
    if GRAPHS is None: return jsonify(
        {"status": "error", "message": "Server not ready; call /load_network_data first."}), 503
    print("\n--- Received request for /generate_weekday_plan (with route) ---")
    try:
        form_data = request.form
        csv_file, xml_file, second_path = (form_data.get(k) for k in ['csv_file', 'xml_file', 'second_path'])
        if not all([csv_file, xml_file, second_path]): return jsonify(
            {"status": "error", "message": "Missing file path parameters."}), 400

        speeds_kmh = _parse_speeds(form_data)
        generate_weekday_plan_only(csv_file, xml_file, second_path, speeds_kmh, ROUTE_DATA_FOLDER)
        print("✅ Weekday plan update (with route) finished successfully.")
        return jsonify({"status": "success", "message": "Weekday plan update task completed."})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"An exception occurred: {str(e)}"}), 500


@app.route('/generate_full_plan_without_route', methods=['POST'])
def handle_full_plan_generation_without_route():
    """Route 4: Generate full plan (without route). Does NOT require /load_network_data."""
    print("\n--- Received request for /generate_full_plan_without_route ---")
    try:
        form_data = request.form
        csv_file, xml_file, second_path = (form_data.get(k) for k in ['csv_file', 'xml_file', 'second_path'])
        if not all([csv_file, xml_file, second_path]): return jsonify(
            {"status": "error", "message": "Missing file path parameters."}), 400

        speeds_kmh = _parse_speeds(form_data)
        detour_factors = _parse_detour_factors(form_data)
        print(f"Using detour factors: {detour_factors}")

        generate_full_plan_without_route(csv_file, xml_file, second_path, speeds_kmh, detour_factors)

        print("✅ Full plan generation (without route) finished successfully.")
        return jsonify({"status": "success", "message": "Full plan generation (without route) task completed."})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"An exception occurred: {str(e)}"}), 500


@app.route('/generate_weekday_plan_without_route', methods=['POST'])
def handle_weekday_plan_update_without_route():
    """Route 5: Update weekday plan only (without route). Does NOT require /load_network_data."""
    print("\n--- Received request for /generate_weekday_plan_without_route ---")
    try:
        form_data = request.form
        csv_file, xml_file, second_path = (form_data.get(k) for k in ['csv_file', 'xml_file', 'second_path'])
        if not all([csv_file, xml_file, second_path]): return jsonify(
            {"status": "error", "message": "Missing file path parameters."}), 400

        speeds_kmh = _parse_speeds(form_data)
        detour_factors = _parse_detour_factors(form_data)
        print(f"Using detour factors: {detour_factors}")

        generate_weekday_plan_only_without_route(csv_file, xml_file, second_path, speeds_kmh, detour_factors)

        print("✅ Weekday plan update (without route) finished successfully.")
        return jsonify({"status": "success", "message": "Weekday plan update (without route) task completed."})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"An exception occurred: {str(e)}"}), 500


@app.route('/delete_plans', methods=['POST'])
def handle_plan_deletion():
    """Route 6: Delete plans for specified persons."""
    print("\n--- Received request for /delete_plans ---")
    try:
        csv_path, main_path, second_path = (request.form.get(k) for k in
                                            ['updated_csv', 'main_output_path', 'second_output_path'])
        if not all([csv_path, main_path, second_path]): return jsonify(
            {"status": "error", "message": "Missing parameters."}), 400
        remove_persons_from_xml(csv_path, main_path, second_path)
        print("✅ Plan deletion task finished successfully.")
        return jsonify({"status": "success", "message": "Plan deletion task completed."})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"An exception occurred: {str(e)}"}), 500


@app.route('/generate_year_end_plan', methods=['POST'])
def handle_generate_year_end_plan():
    """Route 7: Process year-end changes (with route). Requires /load_network_data first."""
    if ROUTE_DATA_FOLDER is None: return jsonify(
        {"status": "error", "message": "Server not ready; call /load_network_data first."}), 503
    print("\n--- Received request for /generate_year_end_plan ---")
    try:
        form_data = request.form
        csv_file, xml_file, second_path = (form_data.get(k) for k in ['csv_file', 'xml_file', 'second_path'])
        if not all([csv_file, xml_file, second_path]): return jsonify(
            {"status": "error", "message": "Missing parameters for year-end processing."}), 400

        speeds_kmh = _parse_speeds(form_data)
        generate_year_end_plan(csv_path=csv_file, xml_path=xml_file, xml_second_path=second_path,
                               data_folder=ROUTE_DATA_FOLDER, speeds_kmh=speeds_kmh)
        print("✅ Year-end processing task (with route) finished successfully.")
        return jsonify({"status": "success", "message": "Year-end processing task (with route) completed."})
    except Exception as e:
        traceback.print_exc()
        return jsonify(
            {"status": "error", "message": f"An exception occurred during year-end processing: {str(e)}"}), 500


@app.route('/generate_year_end_plan_without_route', methods=['POST'])
def handle_generate_year_end_plan_without_route():
    """Route 8: Process year-end changes (without route). Does NOT require /load_network_data."""
    print("\n--- Received request for /generate_year_end_plan_without_route ---")
    try:
        form_data = request.form
        csv_file, xml_file, second_path = (form_data.get(k) for k in ['csv_file', 'xml_file', 'second_path'])
        if not all([csv_file, xml_file, second_path]): return jsonify(
            {"status": "error", "message": "Missing parameters for year-end processing."}), 400

        speeds_kmh = _parse_speeds(form_data)
        detour_factors = _parse_detour_factors(form_data)
        print(f"Using detour factors: {detour_factors}")

        generate_year_end_plan_without_route(csv_path=csv_file, xml_path=xml_file, xml_second_path=second_path,
                                          speeds_kmh=speeds_kmh, detour_factors=detour_factors)
        print("✅ Year-end processing task (without route) finished successfully.")
        return jsonify({"status": "success", "message": "Year-end processing task (without route) completed."})
    except Exception as e:
        traceback.print_exc()
        return jsonify(
            {"status": "error", "message": f"An exception occurred during year-end processing: {str(e)}"}), 500


if __name__ == '__main__':
    print("Python server is running...")
    app.run(host='127.0.0.1', port=5000, debug=False)

