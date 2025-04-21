import xml.etree.ElementTree as ET
import pandas as pd
from geopy.distance import geodesic

def calculate_duration(start_time, end_time):
    if start_time is None or end_time is None:
        return None
    start = pd.to_datetime(start_time, format="%H:%M:%S")
    end = pd.to_datetime(end_time, format="%H:%M:%S")
    if end < start:
        end += pd.Timedelta(days=1)
    return (end - start).total_seconds()

def calculate_distance(coord1, coord2):
    if None in coord1 or None in coord2:
        return None
    return geodesic(coord1, coord2).kilometers

# Define bins and mode list globally
distance_bins = [0, 2, 5, 10, 20, float("inf")]
distance_labels = ["<2km", "2-5km", "5-10km", "10-20km", ">20km"]
mode_order = ["Bus", "Private_vehicle", "Subway", "Taxi", "Two_wheels", "Walking", "For-Hire Vehicle"]

# Load XML file
file_path = "Scenarios/Beijing/Daily Plan/DailyPlan.xml"
tree = ET.parse(file_path)
root = tree.getroot()

weekday_data, weekend_data = [], []

# Parse
for person in root.findall("person"):
    pid = person.get("ID")
    for plan in person.findall("plan"):
        plan_type = plan.get("type")
        activities = plan.findall("activity")
        legs = plan.findall("leg")
        last_end_time = "00:00:00"

        for i in range(len(activities)):
            activity = activities[i]
            activity_type = activity.get("type")
            facility_id = activity.get("facilityID").replace("Residential ", "").replace("Businessmen ", "")
            end_time = activity.get("end_time") if i != len(activities) - 1 else None
            mode = legs[i - 1].get("mode") if i > 0 else None
            travel_time = legs[i].get("trav_time") if i < len(legs) else None

            coordinates = (float(activity.get("y")), float(activity.get("x")))
            if i == 0 and legs:
                mode = legs[0].get("mode")
            if i == 1 and len(legs) > 1:
                mode = legs[1].get("mode")

            start_time = last_end_time if i != 0 else "00:00:00"
            duration = calculate_duration(start_time, end_time) if end_time else None
            distance_to_next = calculate_distance(coordinates, (
                float(activities[i + 1].get("y")), float(activities[i + 1].get("x")))) if i < len(activities) - 1 else None

            record = [pid, activity_type, facility_id, start_time, end_time, duration, mode, travel_time, distance_to_next]
            (weekday_data if plan_type == "typical weekday" else weekend_data).append(record)

            last_end_time = (pd.to_datetime(end_time, format="%H:%M:%S") + pd.to_timedelta(travel_time if travel_time else "00:00:00")).strftime("%H:%M:%S") if end_time else None

# Save activity CSVs
columns = ["PID", "Activity Type", "Facility ID", "Start Time", "End Time", "Duration (seconds)", "Mode", "Travel Time", "Distance to Next (km)"]
weekday_df = pd.DataFrame(weekday_data, columns=columns)
weekday_df.to_csv("typical_weekday_activities.csv", index=False)

if weekend_data:
    weekend_df = pd.DataFrame(weekend_data, columns=columns)
    weekend_df.to_csv("typical_weekend_activities.csv", index=False)

# Assign Vehicle Owner tag
weekday_df["Vehicle Owner"] = weekday_df.groupby("PID")["Mode"].transform(lambda x: "Private_vehicle" in x.values).astype(bool)
if weekend_data:
    weekend_df["Vehicle Owner"] = weekend_df.groupby("PID")["Mode"].transform(lambda x: "Private_vehicle" in x.values).astype(bool)

# Shopping & Leisure Distribution Function
def compute_distance_distribution(df, activity_type, filename):
    filtered_df = df[df["Activity Type"] == activity_type].copy()
    filtered_df["Distance to Next (km)"] = pd.to_numeric(filtered_df["Distance to Next (km)"], errors="coerce")
    filtered_df["Distance Category"] = pd.cut(filtered_df["Distance to Next (km)"], bins=distance_bins, labels=distance_labels, right=False)
    distribution = filtered_df["Distance Category"].value_counts(normalize=True).reindex(distance_labels, fill_value=0)
    distribution_df = distribution.reset_index()
    distribution_df.columns = ["Distance Category", "Probability"]
    distribution_df.to_csv(filename, index=False)
    print(f"Generated: {filename}")

# Mode Choice Distribution Function
def compute_mode_distribution(df, is_vehicle_owner, filename):
    if "Vehicle Owner" not in df.columns:
        raise ValueError("Vehicle Owner column missing.")
    filtered_df = df[df["Vehicle Owner"] == is_vehicle_owner].copy()
    if filtered_df.empty:
        print(f"Skipping {filename}, no data.")
        return
    filtered_df["Distance to Next (km)"] = pd.to_numeric(filtered_df["Distance to Next (km)"], errors="coerce")
    filtered_df["Distance Category"] = pd.cut(filtered_df["Distance to Next (km)"], bins=distance_bins, labels=distance_labels, right=False)
    distribution = filtered_df.groupby(["Distance Category", "Mode"]).size().unstack(fill_value=0)
    distribution = distribution.reindex(columns=mode_order, fill_value=0)
    distribution.to_csv(filename)
    print(f"Generated: {filename}")

# Generate distributions
compute_distance_distribution(weekday_df, "shop", "weekday_shopping_distribution.csv")
compute_distance_distribution(weekday_df, "leisure", "weekday_leisure_distribution.csv")
compute_mode_distribution(weekday_df, True, "weekday_vehicle_choice.csv")
compute_mode_distribution(weekday_df, False, "weekday_non_vehicle_choice.csv")

if weekend_data:
    compute_distance_distribution(weekend_df, "shop", "weekend_shopping_distribution.csv")
    compute_distance_distribution(weekend_df, "leisure", "weekend_leisure_distribution.csv")
    compute_mode_distribution(weekend_df, True, "weekend_vehicle_choice.csv")
    compute_mode_distribution(weekend_df, False, "weekend_non_vehicle_choice.csv")

print("All CSV files generated successfully.")
