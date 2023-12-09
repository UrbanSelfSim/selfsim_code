#part building
import numpy as np
import matplotlib.pyplot as plt
import csv
import os
import shutil
from datetime import datetime
#from statsmodels.nonparametric.kernel_density import KDEMultivariate
import matplotlib.pyplot as plt

current_time = datetime.now()
plt.rcParams.update({'font.size': 20})
folder_name = "png Result output time" + current_time.strftime("%Y-%m-%d-%H-%M-%S")

base_map_path = "basemap/浅灰底图.png"
base_map = plt.imread(base_map_path)
base_map_extent = [113.717732, 114.640673, 22.383916, 22.869296]


try:
    os.mkdir(folder_name)
    print(f"finish：{folder_name}")
except FileExistsError:
    print(f"{folder_name} Folder already exists")



years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
         2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030,
         2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041,
         2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050, 2051, 2052, 2053]

for year in years:
    filename = f'popline{year}year.csv'
    coordinates = []
    zero_count = 0
    if os.path.exists(filename):
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            shutil.copy2(filename, folder_name)
            x1cor_index = header.index('livelong')
            y1cor_index = header.index('livelat')
            x2cor_index = header.index('wslong')
            y2cor_index = header.index('wslat')

            for row in reader:
                if len(row) >= max(x1cor_index, y1cor_index, x2cor_index, y2cor_index) + 1:
                    x1cor = float(row[x1cor_index])
                    y1cor = float(row[y1cor_index])
                    x2cor = float(row[x2cor_index])
                    y2cor = float(row[y2cor_index])
                    
                    # wslong和wslat不为0
                    if x2cor != 0 or y2cor != 0:
                        coordinates.append((x1cor, y1cor, x2cor, y2cor))
                    else:
                        zero_count += 1 

        print(f"{year} Year, There are {zero_count} individuals without jobs")
        plt.figure(figsize=(92, 50))
        plt.imshow(base_map, extent=base_map_extent)
        #连线
        for coords in coordinates:
            x1, y1, x2, y2 = coords
            plt.plot([x1, x2], [y1, y2], marker='o', color='#00008B')


        plt.title(f'moving map ({year}年)')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')

        chart_filename = os.path.join(folder_name, f'moving map {year}.png')
        plt.savefig(chart_filename)
        plt.close()

