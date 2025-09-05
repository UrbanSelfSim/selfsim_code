import os
import re
import shutil
import random
import subprocess
import glob
from datetime import datetime

#%% Create timestamped folder
current_time = datetime.now()
folder_name = "png_output_time_" + current_time.strftime("%Y-%m-%d-%H-%M-%S")
try:
    os.mkdir(folder_name)
    print(f"Folder created: {folder_name}")
except FileExistsError:
    print(f"{folder_name} folder already exists")

# Get current working directory
current_directory = os.getcwd()

# Get the path of the Visualize Code Library
library_path = os.path.join(current_directory, 'Visualize Code Library')

# Get all CSV files
csv_files = [file for file in os.listdir(current_directory) if file.endswith('.csv')]

for csv_file in csv_files:
    source_path = os.path.join(current_directory, csv_file)
    destination_path = os.path.join(library_path, csv_file)

    shutil.copy(source_path, destination_path)

#%% Modify base map file
base_map_path = "basemap/BJXZ.shp"
# If there is only one CSV file in the results, it may indicate an issue with the base map file setting

# Configuration switches
people = 0
people_BEV = 0
people_CV = 0
people_PHEV = 0
residences = 1
OBs = 0
firms = 0
energy_consumption = 0
employees = 0
social_network = 0
social_ave_friend = 0  # Historical line chart
GIF = 1  # Animated chart
line = 0  # Line chart

#%% Execute Transfer_map.py
library_folder = os.path.join(os.getcwd(), "Visualize Code Library")
file_path = os.path.join(library_folder, "Transfer_map.py")

if os.path.exists(file_path):
    subprocess.run(["python", file_path])
else:
    print("?")

#%% energy_consumption.py reads energy consumption coordinate series CSV
if energy_consumption == 1:
    visualize_library_path = 'Visualize Code Library'
    if os.path.exists(visualize_library_path):
        pattern = re.compile(r'.*Energy.*year.*\.csv')
        csv_files = [file for file in os.listdir(visualize_library_path) if pattern.match(file)]

        if csv_files:
            process = subprocess.run(['python', os.path.join(visualize_library_path, 'energy_consumption.py')],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)

            print(process.stdout)

            if process.stderr:
                print(process.stderr)

            print('Completed visualization for energy consumption series')
        else:
            print('No matching energy consumption CSV files found')
    else:
        print('Visualize Code Library subfolder does not exist')
else:
    print('Energy consumption CSV visualization is disabled')

#%% people.py reads people coordinate series CSV
if people == 1:
    visualize_library_path = 'Visualize Code Library'
    if os.path.exists(visualize_library_path):
        pattern = re.compile(r'.*people.*year.*\.csv')
        csv_files = [file for file in os.listdir(visualize_library_path) if pattern.match(file)]

        if csv_files:
            process = subprocess.run(['python', os.path.join(visualize_library_path, 'people.py')],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)

            print(process.stdout)

            if process.stderr:
                print(process.stderr)

            print('Completed visualization for people series')
        else:
            print('No matching people CSV files found')
    else:
        print('Visualize Code Library subfolder does not exist')
else:
    print('People CSV visualization is disabled')

#%% BEV visualization for electric vehicles
if people_BEV == 1:
    visualize_library_path = 'Visualize Code Library'
    if os.path.exists(visualize_library_path):
        pattern = re.compile(r'.*people.*year.*\.csv')
        csv_files = [file for file in os.listdir(visualize_library_path) if pattern.match(file)]

        if csv_files:
            random_csv_file = random.choice(csv_files)
            csv_file_path = os.path.join(visualize_library_path, random_csv_file)

            # Read the header of the CSV file
            with open(csv_file_path, 'r') as file:
                header = file.readline().strip()

            # Check if the header contains BEV field
            if 'BEV' in header:
                process = subprocess.run(['python', os.path.join(visualize_library_path, 'people BEV.py')],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         text=True)

                print(process.stdout)

                if process.stderr:
                    print(process.stderr)

                print('Completed visualization for people BEV series')
            else:
                print('people.csv is missing the BEV field')
        else:
            print('No matching people CSV files found')
    else:
        print('Visualize Code Library subfolder does not exist')
else:
    print('People BEV visualization is disabled')

#%% CV visualization for electric vehicles
if people_CV == 1:
    visualize_library_path = 'Visualize Code Library'
    if os.path.exists(visualize_library_path):
        pattern = re.compile(r'.*people.*year.*\.csv')
        csv_files = [file for file in os.listdir(visualize_library_path) if pattern.match(file)]

        if csv_files:
            random_csv_file = random.choice(csv_files)
            csv_file_path = os.path.join(visualize_library_path, random_csv_file)

            # Read the header of the CSV file
            with open(csv_file_path, 'r') as file:
                header = file.readline().strip()

            # Check if the header contains CV field
            if 'CV' in header:
                process = subprocess.run(['python', os.path.join(visualize_library_path, 'people CV.py')],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         text=True)

                print(process.stdout)

                if process.stderr:
                    print(process.stderr)

                print('Completed visualization for people CV series')
            else:
                print('people.csv is missing the CV field')
        else:
            print('No matching people CSV files found')
    else:
        print('Visualize Code Library subfolder does not exist')
else:
    print('People CV visualization is disabled')

#%% PHEV visualization for electric vehicles
if people_PHEV == 1:
    visualize_library_path = 'Visualize Code Library'
    if os.path.exists(visualize_library_path):
        pattern = re.compile(r'.*people.*year.*\.csv')
        csv_files = [file for file in os.listdir(visualize_library_path) if pattern.match(file)]

        if csv_files:
            random_csv_file = random.choice(csv_files)
            csv_file_path = os.path.join(visualize_library_path, random_csv_file)

            # Read the header of the CSV file
            with open(csv_file_path, 'r') as file:
                header = file.readline().strip()

            # Check if the header contains PHEV field
            if 'PHEV' in header:
                process = subprocess.run(['python', os.path.join(visualize_library_path, 'people PHEV.py')],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         text=True)

                print(process.stdout)

                if process.stderr:
                    print(process.stderr)

                print('Completed visualization for people PHEV series')
            else:
                print('people.csv is missing the PHEV field')
        else:
            print('No matching people CSV files found')
    else:
        print('Visualize Code Library subfolder does not exist')
else:
    print('People PHEV visualization is disabled')

#%% Residences visualization
if residences == 1:
    visualize_library_path = 'Visualize Code Library'
    if os.path.exists(visualize_library_path):
        pattern = re.compile(r'.*residences.*year.*\.csv')
        csv_files = [file for file in os.listdir(visualize_library_path) if pattern.match(file)]

        if csv_files:
            process = subprocess.run(['python', os.path.join(visualize_library_path, 'residences.py')],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)

            print(process.stdout)

            if process.stderr:
                print(process.stderr)

            print('Completed visualization for residences series')
        else:
            print('No matching residences CSV files found')
    else:
        print('Visualize Code Library subfolder does not exist')
else:
    print('Residences CSV visualization is disabled')

#%% OBs visualization
if OBs == 1:
    visualize_library_path = 'Visualize Code Library'
    if os.path.exists(visualize_library_path):
        pattern = re.compile(r'.*OBs.*year.*\.csv')
        csv_files = [file for file in os.listdir(visualize_library_path) if pattern.match(file)]

        if csv_files:
            process = subprocess.run(['python', os.path.join(visualize_library_path, 'OBs.py')],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)

            print(process.stdout)

            if process.stderr:
                print(process.stderr)

            print('Completed visualization for OBs series')
        else:
            print('No matching OBs CSV files found')
    else:
        print('Visualize Code Library subfolder does not exist')
else:
    print('OBs visualization is disabled')
