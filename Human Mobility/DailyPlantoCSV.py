#Parts of the code in this model were generated with the assistance of AI and subsequently revised and validated by the author.

import xml.etree.ElementTree as ET
import pandas as pd
from geopy.distance import geodesic
import argparse
import os


def calculate_duration(start_time, end_time):
    """Calculates the duration in seconds between two H:M:S timestamps."""
    if start_time is None or end_time is None:
        return None
    start = pd.to_datetime(start_time, format="%H:%M:%S")
    end = pd.to_datetime(end_time, format="%H:%M:%S")
    # Handle plans that cross midnight
    if end < start:
        end += pd.Timedelta(days=1)
    return (end - start).total_seconds()


def calculate_distance_from_coords(coord1, coord2):
    """Calculates the geodesic distance in kilometers between two (lat, lon) points."""
    if None in coord1 or None in coord2:
        return None
    return geodesic(coord1, coord2).kilometers


# Standardized mode names to ensure consistency in analysis
mode_order = ["Bus", "Subway", "Taxi", "Two_wheels", "Walk", "For-hire_vehicle", "Private_vehicle"]

# Define distance categories for analysis
distance_bins = [0, 2, 5, 10, 20, float("inf")]
distance_labels = ["<2km", "2-5km", "5-10km", "10-20km", ">20km"]

# --- Main Script Logic ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Universally parse Daily Plan XML (with or without route details) and generate analysis CSVs.")
    parser.add_argument('--input', required=True, help='Path to the input DailyPlan.xml file.')
    parser.add_argument('--output_dir', required=True, help='Directory to save the output CSV files.')
    args = parser.parse_args()

    file_path = args.input
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    print(f"Parsing XML file: {file_path}")
    tree = ET.parse(file_path)
    root = tree.getroot()

    weekday_data, weekend_data = [], []

    for person in root.findall("person"):
        pid = person.get("ID")
        for plan in person.findall("plan"):
            plan_type = plan.get("type")
            activities = plan.findall("activity")
            legs = plan.findall("leg")

            last_activity_end_time = "00:00:00"

            for i in range(len(activities)):
                activity = activities[i]
                activity_type = activity.get("type")

                # Standardized Facility ID parsing
                facility_id_raw = activity.get("facilityID")
                facility_id = facility_id_raw.replace("RF ", "").replace("Businessmen ", "")

                end_time = activity.get("end_time")
                coordinates = (float(activity.get("y")), float(activity.get("x")))

                if i < len(legs):
                    leg = legs[i]
                    mode = leg.get("mode")
                    travel_time = leg.get("trav_time")
                    next_activity = activities[i + 1]

                    # --- UNIVERSAL DISTANCE LOGIC ---
                    distance_to_next = None
                    route_element = leg.find("route")

                    # Priority 1: Try to get distance from the <route> tag
                    if route_element is not None and route_element.get("distance") is not None:
                        try:
                            distance_val = float(route_element.get("distance"))
                            # Heuristic: if value is large, assume meters; otherwise, km.
                            if distance_val > 1000:
                                distance_to_next = distance_val / 1000.0  # Convert meters to km
                            else:
                                distance_to_next = distance_val  # Assume it's already in km
                        except (ValueError, TypeError):
                            # If conversion fails, fall back to calculation
                            distance_to_next = calculate_distance_from_coords(coordinates, (
                            float(next_activity.get("y")), float(next_activity.get("x"))))
                    else:
                        # Priority 2 (Fallback): Calculate distance from coordinates
                        distance_to_next = calculate_distance_from_coords(coordinates, (
                        float(next_activity.get("y")), float(next_activity.get("x"))))

                else:  # This is the last activity, no subsequent leg
                    mode = None
                    travel_time = None
                    distance_to_next = None

                start_time = last_activity_end_time
                duration = calculate_duration(start_time, end_time)

                record = [pid, activity_type, facility_id, start_time, end_time, duration, mode, travel_time,
                          distance_to_next]

                if "weekday" in plan_type:
                    weekday_data.append(record)
                else:
                    weekend_data.append(record)

                if end_time and travel_time:
                    end_dt = pd.to_datetime(end_time, format="%H:%M:%S")
                    travel_td = pd.to_timedelta(travel_time)
                    last_activity_end_time = (end_dt + travel_td).strftime("%H:%M:%S")

    # Create and save the main activity DataFrames
    columns = ["PID", "Activity Type", "Facility ID", "Start Time", "End Time", "Duration (seconds)", "Mode",
               "Travel Time", "Distance to Next (km)"]
    weekday_df = pd.DataFrame(weekday_data, columns=columns)
    weekday_df.to_csv(os.path.join(output_dir, "typical_weekday_activities.csv"), index=False)
    print(f"Generated: {os.path.join(output_dir, 'typical_weekday_activities.csv')}")

    if weekend_data:
        weekend_df = pd.DataFrame(weekend_data, columns=columns)
        weekend_df.to_csv(os.path.join(output_dir, "typical_weekend_activities.csv"), index=False)
        print(f"Generated: {os.path.join(output_dir, 'typical_weekend_activities.csv')}")


    # --- Analysis Functions ---
    def compute_distance_distribution(df, activity_type, filename):
        filtered_df = df[df["Activity Type"] == activity_type].copy()
        if filtered_df.empty:
            print(f"Skipping {filename}, no data for activity '{activity_type}'.")
            return
        filtered_df["Distance Category"] = pd.cut(filtered_df["Distance to Next (km)"], bins=distance_bins,
                                                  labels=distance_labels, right=False)
        distribution = filtered_df["Distance Category"].value_counts(normalize=True).reindex(distance_labels,
                                                                                             fill_value=0)
        distribution_df = distribution.reset_index()
        distribution_df.columns = ["Distance Category", "Probability"]
        distribution_df.to_csv(filename, index=False)
        print(f"Generated: {filename}")


    def compute_mode_distribution(df, is_vehicle_owner_col, filename):
        filtered_df = df[df["Vehicle Owner"] == is_vehicle_owner_col].copy()
        if filtered_df.empty:
            print(f"Skipping {filename}, no data for vehicle owner status: {is_vehicle_owner_col}.")
            return
        filtered_df["Distance Category"] = pd.cut(filtered_df["Distance to Next (km)"], bins=distance_bins,
                                                  labels=distance_labels, right=False)
        distribution = filtered_df.groupby(["Distance Category", "Mode"]).size().unstack(fill_value=0)
        distribution = distribution.reindex(columns=mode_order, fill_value=0)
        distribution.to_csv(filename)
        print(f"Generated: {filename}")


    # --- Run Analysis ---
    weekday_df["Vehicle Owner"] = weekday_df.groupby("PID")["Mode"].transform(lambda x: "Private_vehicle" in x.values)

    compute_distance_distribution(weekday_df, "shopping", os.path.join(output_dir, "weekday_shopping_distribution.csv"))
    compute_distance_distribution(weekday_df, "leisure", os.path.join(output_dir, "weekday_leisure_distribution.csv"))
    compute_mode_distribution(weekday_df, True, os.path.join(output_dir, "weekday_vehicle_choice.csv"))
    compute_mode_distribution(weekday_df, False, os.path.join(output_dir, "weekday_non_vehicle_choice.csv"))

    if weekend_data:
        weekend_df["Vehicle Owner"] = weekend_df.groupby("PID")["Mode"].transform(
            lambda x: "Private_vehicle" in x.values)
        compute_distance_distribution(weekend_df, "shopping",
                                      os.path.join(output_dir, "weekend_shopping_distribution.csv"))
        compute_distance_distribution(weekend_df, "leisure",
                                      os.path.join(output_dir, "weekend_leisure_distribution.csv"))
        compute_mode_distribution(weekend_df, True, os.path.join(output_dir, "weekend_vehicle_choice.csv"))
        compute_mode_distribution(weekend_df, False, os.path.join(output_dir, "weekend_non_vehicle_choice.csv"))

    print("\nAll CSV files generated successfully.")
