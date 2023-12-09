#part building
import numpy as np
import matplotlib.pyplot as plt
import csv
import os
import shutil
from datetime import datetime

current_time = datetime.now()
plt.rcParams.update({'font.size': 20})
folder_name = "png Result output time" + current_time.strftime("%Y-%m-%d-%H-%M-%S")

try:
    os.mkdir(folder_name)
    print(f"完成：{folder_name}")
except FileExistsError:
    print(f"{folder_name} 文件夹已存在")

# 替代的 PNG 底图路径
base_map_path = "basemap/浅灰底图.png"
base_map = plt.imread(base_map_path)

base_map_extent = [113.717732, 114.640673, 22.383916, 22.869296]  # 根据底图坐标范围设置

years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
         2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030,
         2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041,
         2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050, 2051, 2052, 2053]

for year in years:
    filename = f'residences{year}year.csv'
    coordinates = []
    house_prices = []  # 第三属性值
    if os.path.exists(filename):
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            shutil.copy2(filename, folder_name)
            xcor_index = header.index('x-coordinate')
            ycor_index = header.index('y-coordinate')
            house_price_index = header.index('House-price')  # 第三属性值属性名

            for row in reader:
                if len(row) >= max(xcor_index, ycor_index, house_price_index) + 1:
                    xcor = float(row[xcor_index])
                    ycor = float(row[ycor_index])
                    house_price = float(row[house_price_index])  # 读取第三属性值
                    coordinates.append((xcor, ycor))
                    house_prices.append(house_price)

    if coordinates:
        plt.figure(figsize=(92, 50))
        plt.imshow(base_map, extent=base_map_extent, aspect='auto')
        plt.title(f'{year} Residences House-price Point Plot')

        scaled_house_prices = np.array(house_prices) / 400  # 缩小1000倍
        label_house_prices = np.array(house_prices)
        max_house_price = max(scaled_house_prices)
        normalized_house_prices = scaled_house_prices / max_house_price  # 根据最大价格进行归一化

        for (x, y), normalized_price, scaled_house_price, label_house_price in zip(coordinates, normalized_house_prices, scaled_house_prices, label_house_prices):
            color = plt.cm.coolwarm(normalized_price)
            plt.scatter(x, y, marker='.', c=color, s=scaled_house_price, alpha=1, cmap='coolwarm')
            plt.text(x, y, f'{label_house_price:.2f}', color='black', fontsize=10, ha='center', va='center')
        """  
        barstyle = plt.cm.ScalarMappable(cmap='coolwarm', norm=plt.Normalize(0, 1))
        barstyle.set_array([])
        cbar = plt.colorbar(barstyle, label='Residences prices')
        cbar.set_ticks([0, 1])
        cbar.set_ticklabels(['min', 'max'])
        """
        subfolder_path = os.path.join(".", folder_name)
        os.makedirs(subfolder_path, exist_ok=True)
        save_path = os.path.join(subfolder_path, f"{year}Residences House-price.png")
        plt.xlabel('X coordinate')
        plt.ylabel('Y coordinate')
        plt.savefig(save_path)
        plt.close()

plt.show()
#%%
plt.rcParams.update({'font.size': 20})

# 将您的shapefile加载为GeoDataFrame
base_map_path = "basemap/浅灰底图.png"
base_map = plt.imread(base_map_path)

years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
         2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030,
         2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041,
         2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050, 2051, 2052, 2053]

for year in years:
    filename = f'residences{year}year.csv'
    coordinates = []
    House_rents = []  # 第三属性值
    if os.path.exists(filename):
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            shutil.copy2(filename, folder_name)
            xcor_index = header.index('x-coordinate')
            ycor_index = header.index('y-coordinate')
            House_rent_index = header.index('House-rent')  # 第三属性值属性名

            for row in reader:
                if len(row) >= max(xcor_index, ycor_index, house_price_index) + 1:
                    xcor = float(row[xcor_index])
                    ycor = float(row[ycor_index])
                    House_rent = float(row[House_rent_index])  # 读取第三属性值
                    coordinates.append((xcor, ycor))
                    House_rents.append(House_rent)


    if coordinates:
        plt.figure(figsize=(92, 50))
        #base_map.plot(ax=plt.gca(), color='white', alpha=1.0, edgecolor='black', linewidth=0.5)
        plt.imshow(base_map, extent=base_map_extent, aspect='auto')
        plt.title(f'{year} Residences House-rent Point Plot')

        scaled_House_rents = np.array(House_rents) / 5  # 缩小所需
        label_House_rents = np.array(House_rents)
        max_House_rent = max(scaled_House_rents)
        normalized_House_rents = scaled_House_rents / max_House_rent  # 归一化

        for (x, y), normalized_House_rents,scaled_House_rents, label_House_rents in zip(coordinates, normalized_House_rents, scaled_House_rents, label_House_rents):
            color = plt.cm.coolwarm(normalized_House_rents)
            plt.scatter(x, y, marker='.', c=color, s=scaled_House_rents, alpha=1, cmap='coolwarm')
            plt.text(x, y, f'{label_House_rents:.2f}', color='black', fontsize=10, ha='center', va='center')

        """
        barstyle = plt.cm.ScalarMappable(cmap='coolwarm', norm=plt.Normalize(0, 1))  # unless
        barstyle.set_array([])
        cbar = plt.colorbar(barstyle, label='Residences rent')
        cbar.set_ticks([0, 1])
        cbar.set_ticklabels(['min', 'max'])
        """
    
        subfolder_path = os.path.join(".", folder_name)
        os.makedirs(subfolder_path, exist_ok=True)
        save_path = os.path.join(subfolder_path, f"{year}Residences House-rent.png")
        plt.xlabel('X coordinate')
        plt.ylabel('Y coordinate')
        plt.savefig(save_path)
        plt.close()

plt.show()



#%%
plt.rcParams.update({'font.size': 20})

# 将您的shapefile加载为GeoDataFrame
base_map_path = "basemap/浅灰底图.png"
base_map = plt.imread(base_map_path)

years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
         2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030,
         2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041,
         2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050, 2051, 2052, 2053]

for year in years:
    filename = f'schools{year}year.csv'
    coordinates = []
    Num_students = []  # 第三属性值
    if os.path.exists(filename):
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            shutil.copy2(filename, folder_name)
            xcor_index = header.index('x-coordinate')
            ycor_index = header.index('y-coordinate')
            Num_student_index = header.index('Num-student')  # 第三属性值属性名

            for row in reader:
                if len(row) >= max(xcor_index, ycor_index, house_price_index) + 1:
                    xcor = float(row[xcor_index])
                    ycor = float(row[ycor_index])
                    Num_student = float(row[Num_student_index])  # 读取第三属性值
                    coordinates.append((xcor, ycor))
                    Num_students.append(Num_student)


    if coordinates:
        plt.figure(figsize=(92, 50))
        #base_map.plot(ax=plt.gca(), color='white', alpha=1.0, edgecolor='black', linewidth=0.5)
        plt.imshow(base_map, extent=base_map_extent, aspect='auto')
        plt.title(f'{year} School Num-student Point Plot')

        scaled_Num_students = np.array(Num_students) *10  # 缩放所需
        label_Num_students = np.array(Num_students)
        max_Num_student = max(scaled_Num_students)
        normalized_Num_students = scaled_Num_students / max_Num_student  # 归一化

        for (x, y), normalized_Num_students,scaled_Num_students, label_Num_students in zip(coordinates, normalized_Num_students, scaled_Num_students, label_Num_students):
            color = plt.cm.coolwarm(normalized_Num_students)
            plt.scatter(x, y, marker='.', c=color, s=scaled_Num_students, alpha=1, cmap='coolwarm')
            plt.text(x, y, f'{label_Num_students:.2f}', color='black', fontsize=10, ha='center', va='center')

        """
        barstyle = plt.cm.ScalarMappable(cmap='coolwarm', norm=plt.Normalize(0, 1))  # unless
        barstyle.set_array([])
        cbar = plt.colorbar(barstyle, label='School Num-student')
        cbar.set_ticks([0, 1])
        cbar.set_ticklabels(['min', 'max'])
        """
    
        subfolder_path = os.path.join(".", folder_name)
        os.makedirs(subfolder_path, exist_ok=True)
        save_path = os.path.join(subfolder_path, f"{year}School Num-student.png")
        plt.xlabel('X coordinate')
        plt.ylabel('Y coordinate')
        plt.savefig(save_path)
        plt.close()

plt.show()
#%%
plt.rcParams.update({'font.size': 20})

# 将您的shapefile加载为GeoDataFrame
base_map_path = "basemap/浅灰底图.png"
base_map = plt.imread(base_map_path)

years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
         2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030,
         2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041,
         2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050, 2051, 2052, 2053]

for year in years:
    filename = f'OBs{year}year.csv'
    coordinates = []
    ob_prices = []  # 第三属性值
    if os.path.exists(filename):
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            shutil.copy2(filename, folder_name)
            xcor_index = header.index('x-coordinate')
            ycor_index = header.index('y-coordinate')
            ob_price_index = header.index('ob-price')  # 第三属性值属性名

            for row in reader:
                if len(row) >= max(xcor_index, ycor_index, house_price_index) + 1:
                    xcor = float(row[xcor_index])
                    ycor = float(row[ycor_index])
                    ob_price = float(row[ob_price_index])  # 读取第三属性值
                    coordinates.append((xcor, ycor))
                    ob_prices.append(ob_price)


    if coordinates:
        plt.figure(figsize=(92, 50))
        #base_map.plot(ax=plt.gca(), color='white', alpha=1.0, edgecolor='black', linewidth=0.5)
        plt.imshow(base_map, extent=base_map_extent, aspect='auto')
        plt.title(f'{year} Office Buildings rent Point Plot')

        scaled_ob_prices = np.array(ob_prices) /100  # 缩放所需
        label_ob_prices = np.array(ob_prices)
        max_ob_price = max(scaled_ob_prices)
        normalized_ob_prices = scaled_ob_prices / max_ob_price  # 归一化

        for (x, y), normalized_ob_prices,scaled_ob_prices, label_ob_prices in zip(coordinates, normalized_ob_prices, scaled_ob_prices, label_ob_prices):
            color = plt.cm.coolwarm(normalized_ob_prices)
            plt.scatter(x, y, marker='.', c=color, s=scaled_ob_prices, alpha=1, cmap='coolwarm')
            plt.text(x, y, f'{label_ob_prices:.2f}', color='black', fontsize=10, ha='center', va='center')

        """
        barstyle = plt.cm.ScalarMappable(cmap='coolwarm', norm=plt.Normalize(0, 1))  # unless
        barstyle.set_array([])
        cbar = plt.colorbar(barstyle, label='OBs rent')
        cbar.set_ticks([0, 1])
        cbar.set_ticklabels(['min', 'max'])
        """
    
        subfolder_path = os.path.join(".", folder_name)
        os.makedirs(subfolder_path, exist_ok=True)
        save_path = os.path.join(subfolder_path, f"{year} Office Buildings rent.png")
        plt.xlabel('X coordinate')
        plt.ylabel('Y coordinate')
        plt.savefig(save_path)
        plt.close()

plt.show()



#%%
#part people
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.nonparametric.kernel_density import KDEMultivariate
from matplotlib.colors import LinearSegmentedColormap
import csv
import os
import shutil
from datetime import datetime
import geopandas as gpd
import mpl_scatter_density

current_time = datetime.now()
plt.rcParams.update({'font.size': 20})
#folder_name = "Result output time" + current_time.strftime("%Y-%m-%d-%H-%M-%S")
try:
    os.mkdir(folder_name)
    print(f"finish：{folder_name}")
except FileExistsError:
    print(f"{folder_name} Folder already exists")

# 将您的shapefile加载为GeoDataFrame
base_map_path = "basemap/浅灰底图.png"
base_map = plt.imread(base_map_path)

base_map_extent = [113.717732, 114.640673, 22.383916, 22.869296]  # 根据底图坐标范围设置

years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
         2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030,
         2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041,
         2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050, 2051, 2052, 2053]

for year in years:
    filename = f'people{year}year.csv'
    coordinates = []
    if os.path.exists(filename):
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            shutil.copy2(filename, folder_name)
            xcor_index = header.index('x-coordinate')
            ycor_index = header.index('y-coordinate')

            for row in reader:
                if len(row) >= max(xcor_index, ycor_index) + 1:  
                    xcor = float(row[xcor_index])
                    ycor = float(row[ycor_index])
                    coordinates.append((xcor, ycor))
    


    if coordinates:
        def generate_density_map(coords, base_map):
            data = np.array(coords)
            x_coords, y_coords = data[:, 0], data[:, 1]
    
            kde = KDEMultivariate(data, var_type='cc', bw='normal_reference')

            x_grid, y_grid = np.mgrid[113.717732:114.640673:500j, 22.383916:22.869296:500j]  # 使用固定的底图范围
            density = kde.pdf(np.column_stack([x_grid.ravel(), y_grid.ravel()]))
            density = density.reshape(x_grid.shape)
    
            plt.figure(figsize=(92, 50))
            plt.imshow(base_map, extent=[113.717732, 114.640673, 22.383916, 22.869296], aspect='auto')  # 使用固定的底图范围
    
            cmap = plt.cm.get_cmap('RdYlGn_r')
            cmap._init()  # 初始化颜色映射
    
            # 获取颜色映射的颜色数组，并对后半段进行透明度设置
            colors = cmap(np.arange(cmap.N))
            colors[:int(cmap.N / 2.5):, 3] = 0  # 将后半段颜色的透明度设为0，使其变为透明
    
            modified_cmap = LinearSegmentedColormap.from_list('Modified_RdYlGn_r', colors)
    
            plt.imshow(density.T, origin='lower', extent=[113.717732, 114.640673, 22.383916, 22.869296],
                       cmap=modified_cmap, alpha=0.8, vmin=density.min(), vmax=density.max())
            """
            plt.colorbar(label='Densities')
            """
            plt.title(f'{year} Population Density map')
            plt.xlabel('X coordinate')
            plt.ylabel('Y coordinate')
    
            subfolder_path = os.path.join(".", folder_name)
            os.makedirs(subfolder_path, exist_ok=True)
            save_path = os.path.join(subfolder_path, f"{year}Density-Map.png")
            plt.savefig(save_path)
            plt.close()


        def generate_heatmap(coords, base_map):
            x_coords, y_coords = zip(*coords)
            
            plt.figure(figsize=(92, 50))
            base_map_extent = [113.717732, 114.640673, 22.383916, 22.869296]  # 新的底图范围
            plt.imshow(base_map, extent=base_map_extent, aspect='equal')  # 修改这里的aspect参数
            
            plt.hist2d(x_coords, y_coords, bins=(50, 50), cmap='hot', alpha=0.7) 
            """
            plt.colorbar(label='Frequency')
            """
            plt.title(f'{year} Population Hotspot map')
            plt.xlabel('X coordinate')
            plt.ylabel('Y coordinate')
            
            subfolder_path = os.path.join(".", folder_name)
            os.makedirs(subfolder_path, exist_ok=True)
            save_path = os.path.join(subfolder_path, f"{year}Hotspot-Map.png")
            plt.savefig(save_path)
            plt.close()
            
            
            
            

        generate_heatmap(coordinates, base_map)
        generate_density_map(coordinates, base_map)

plt.show()  
#%%
from matplotlib.colors import LinearSegmentedColormap
import geopandas as gpd
import mpl_scatter_density
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt

#current_time = datetime.now()
plt.rcParams.update({'font.size': 20})
#folder_name = "png Result output time" + current_time.strftime("%Y-%m-%d-%H-%M-%S")



#current_time = datetime.now()
#plt.rcParams.update({'font.size': 20})
#folder_name = "Result output time" + current_time.strftime("%Y-%m-%d-%H-%M-%S")
try:
    os.mkdir(folder_name)
    print(f"finish：{folder_name}")
except FileExistsError:
    print(f"{folder_name} Folder already exists")

#base_map_extent = [113.717732, 114.640673, 22.383916, 22.869296]  # 根据底图坐标范围设置

years = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019,
         2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030,
         2031, 2032, 2033, 2034, 2035, 2036, 2037, 2038, 2039, 2040, 2041,
         2042, 2043, 2044, 2045, 2046, 2047, 2048, 2049, 2050, 2051, 2052, 2053]

for year in years:
    filename = f'people{year}year.csv'
    coordinates = []
    if os.path.exists(filename):
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            shutil.copy2(filename, folder_name)
            xcor_index = header.index('x-coordinate')
            ycor_index = header.index('y-coordinate')

            for row in reader:
                if len(row) >= max(xcor_index, ycor_index) + 1:  
                    xcor = float(row[xcor_index])
                    ycor = float(row[ycor_index])
                    coordinates.append((xcor, ycor))
    


    if coordinates:
        #print(coordinates)

        x = [coord[0] for coord in coordinates]
        y = [coord[1] for coord in coordinates]
        
        # 读取底图
        base_map_path = "basemap/浅灰底图.png"
        base_map = plt.imread(base_map_path)
        
        # 绘制底图
        fig, ax = plt.subplots(figsize=(92, 50))
        ax.imshow(base_map, extent=[113.717732, 114.640673, 22.383916, 22.869296])
        
        # 使用自定义颜色映射
        cmap = LinearSegmentedColormap.from_list('my_cmap', [(0, 'White'), (1, 'Red')])
        
        hist, xedges, yedges = np.histogram2d(x, y, bins=(100, 100), range=[[113.717732, 114.640673], [22.383916, 22.869296]])
        
        extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
        ax.imshow(hist.T, cmap=cmap, extent=extent, origin='lower', alpha=0.6)
        ax.set_xlim(113.717732, 114.640673)
        ax.set_ylim(22.383916, 22.869296)
        #fig.colorbar(ax.get_images()[0], label='Density', cmap=cmap)
        
        #plt.savefig('scatter_density_with_base_map.png')
        #plt.show()
        
    
        subfolder_path = os.path.join(".", folder_name)
        os.makedirs(subfolder_path, exist_ok=True)
        save_path = os.path.join(subfolder_path, f"{year} Population Hotspot pro.png")
        plt.title(f'{year} Hotspot-Map pro')
        plt.xlabel('X coordinate')
        plt.ylabel('Y coordinate')
        plt.savefig(save_path)
        plt.close()

#%%
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
#folder_name = "png Result output time" + current_time.strftime("%Y-%m-%d-%H-%M-%S")

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


#%%
#清理
import os
import glob
current_directory = os.getcwd()
csv_files = glob.glob(os.path.join(current_directory, '*.csv'))
for csv_file in csv_files:
    file_name = os.path.basename(csv_file)
    if 'year' in file_name:
        os.remove(csv_file)
        print(f"Deleted documents：{file_name}")
        
print("已将原文件移动到输出文件夹，如需再次使用代码，请再次输出代码或将输出后文件移动到原位置")
print("The original file has been moved to the output folder, if you want to use the code again, please output the code again or move the output file to the original location.")

