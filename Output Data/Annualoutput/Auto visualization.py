import os
import re
import shutil
import random
import subprocess
import glob
from datetime import datetime

#%%
current_time = datetime.now()
folder_name = "png_output_time_" + current_time.strftime("%Y-%m-%d-%H-%M-%S")
try:
    os.mkdir(folder_name)
    print(f"已创建文件夹：{folder_name}")
except FileExistsError:
    print(f"{folder_name} 文件夹已存在")
# 获取当前工作目录
current_directory = os.getcwd()

# 获取Visualize Code Library的路径
library_path = os.path.join(current_directory, 'Visualize Code Library')

# 获取所有CSV文件
csv_files = [file for file in os.listdir(current_directory) if file.endswith('.csv')]


for csv_file in csv_files:
    source_path = os.path.join(current_directory, csv_file)
    destination_path = os.path.join(library_path, csv_file)

    shutil.copy(source_path, destination_path)

print("")
#%%
#修改底图文件
base_map_path = "basemap/BJXZ.shp"
#若是结果内只有一个csv文档则可能是底图文件设置有误
#csv读取制图配置 开启请设置为1

people = 0
#电车部分
people_BEV = 0
people_CV = 0
people_PHEV = 0

residences = 1
OBs = 0
firms = 0

energy_consumption = 0
employees = 0

social_network = 0
social_ave_friend = 0 #历年折线图
#功能性配置 开启请设置为1
GIF = 1    #动图
line = 0    #折线图

#%%
library_folder = os.path.join(os.getcwd(), "Visualize Code Library")
file_path = os.path.join(library_folder, "Transfer_map.py")

if os.path.exists(file_path):
    subprocess.run(["python", file_path])
else:
    print("?")

#%%
#energy_consumption.py读取energy_consumption坐标系列csv
# 检测是否有energy_consumption=1
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

            print('已完成energy consumption系列的可视化')
        else:
            print('没有符合条件的energy consumption.csv文件')
    else:
        print('Visualize Code Library子文件夹不存在')
else:
    print('已关闭energy consumption.csv的可视化')


#%%
#people.py读取people坐标系列csv
# 检测是否有people=1
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
            
            print('已完成people系列的可视化')
        else:
            print('没有符合条件的people.csv文件')
    else:
        print('Visualize Code Library子文件夹不存在')
else:
    print('已关闭people.csv的可视化')
#%%
#电车BEV
if people_BEV == 1:
    visualize_library_path = 'Visualize Code Library'
    
    if os.path.exists(visualize_library_path):
        pattern = re.compile(r'.*people.*year.*\.csv')
        csv_files = [file for file in os.listdir(visualize_library_path) if pattern.match(file)]

        if csv_files:
            random_csv_file = random.choice(csv_files)
            csv_file_path = os.path.join(visualize_library_path, random_csv_file)

            # 读取CSV文件的表头
            with open(csv_file_path, 'r') as file:
                header = file.readline().strip()

            # 检查表头是否包含BEV字段
            if 'BEV' in header:
                process = subprocess.run(['python', os.path.join(visualize_library_path, 'people BEV.py')],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         text=True)

                print(process.stdout)

                if process.stderr:
                    print(process.stderr)

                print('已完成people BEV系列的可视化')
            else:
                print('people.csv字段不全，无BEV字段')
        else:
            print('没有符合条件的people.csv文件')
    else:
        print('Visualize Code Library子文件夹不存在')
else:
    print('已关闭people BEV的可视化')
#%%
#电车CV
if people_CV == 1:
    visualize_library_path = 'Visualize Code Library'
    
    if os.path.exists(visualize_library_path):
        pattern = re.compile(r'.*people.*year.*\.csv')
        csv_files = [file for file in os.listdir(visualize_library_path) if pattern.match(file)]

        if csv_files:
            random_csv_file = random.choice(csv_files)
            csv_file_path = os.path.join(visualize_library_path, random_csv_file)

            # 读取CSV文件的表头
            with open(csv_file_path, 'r') as file:
                header = file.readline().strip()

            # 检查表头是否包含CV字段
            if 'CV' in header:
                process = subprocess.run(['python', os.path.join(visualize_library_path, 'people CV.py')],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         text=True)

                print(process.stdout)

                if process.stderr:
                    print(process.stderr)

                print('已完成people CV系列的可视化')
            else:
                print('people.csv字段不全，无CV字段')
        else:
            print('没有符合条件的people.csv文件')
    else:
        print('Visualize Code Library子文件夹不存在')
else:
    print('已关闭people CV的可视化')
#%%
#电车PHEV
if people_PHEV == 1:
    visualize_library_path = 'Visualize Code Library'
    
    if os.path.exists(visualize_library_path):
        pattern = re.compile(r'.*people.*year.*\.csv')
        csv_files = [file for file in os.listdir(visualize_library_path) if pattern.match(file)]

        if csv_files:
            random_csv_file = random.choice(csv_files)
            csv_file_path = os.path.join(visualize_library_path, random_csv_file)

            # 读取CSV文件的表头
            with open(csv_file_path, 'r') as file:
                header = file.readline().strip()

            # 检查表头是否包含PHEV字段
            if 'PHEV' in header:
                process = subprocess.run(['python', os.path.join(visualize_library_path, 'people PHEV.py')],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         text=True)

                print(process.stdout)

                if process.stderr:
                    print(process.stderr)

                print('已完成people PHEV系列的可视化')
            else:
                print('people.csv字段不全，无PHEV字段')
        else:
            print('没有符合条件的people.csv文件')
    else:
        print('Visualize Code Library子文件夹不存在')
else:
    print('已关闭people PHEV的可视化')
#%%
#residences.py读取residences的租金和房价
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
            
            print('已完成residences系列的可视化')
        else:
            print('没有符合条件的residences.csv文件')
    else:
        print('Visualize Code Library子文件夹不存在')
else:
    print('已关闭residences.csv的可视化')
    
#%%
#OBs.py读取OBs的ob-price
# 检测是否有OBs=1
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
            
            print('已完成OBs系列的可视化')
        else:
            print('没有符合条件的OBs.csv文件')
    else:
        print('Visualize Code Library子文件夹不存在')
else:
    print('已关闭OBs.csv的可视化')
#%%
#firms.py读取firms的staff
# 检测是否有firms=1
if firms == 1:
    visualize_library_path = 'Visualize Code Library'
    if os.path.exists(visualize_library_path):
        pattern = re.compile(r'.*firms.*year.*\.csv')
        csv_files = [file for file in os.listdir(visualize_library_path) if pattern.match(file)]

        if csv_files:
            process = subprocess.run(['python', os.path.join(visualize_library_path, 'firms.py')],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)
            
            print(process.stdout)

            if process.stderr:
                print(process.stderr)
            
            print('已完成firms系列的可视化')
        else:
            print('没有符合条件的firms.csv文件')
    else:
        print('Visualize Code Library子文件夹不存在')
else:
    print('已关闭firms.csv的可视化')
#%%
#employees.py读取employees.csv
# 检测是否有employees=1
if employees == 1:
    visualize_library_path = 'Visualize Code Library'
    if os.path.exists(visualize_library_path):
        pattern = re.compile(r'.*employees.*year.*\.csv')
        csv_files = [file for file in os.listdir(visualize_library_path) if pattern.match(file)]

        if csv_files:
            process = subprocess.run(['python', os.path.join(visualize_library_path, 'employees.py')],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     text=True)
            
            print(process.stdout)

            if process.stderr:
                print(process.stderr)
            
            print('已完成employees系列的可视化')
        else:
            print('没有符合条件的employees.csv文件')
    else:
        print('Visualize Code Library子文件夹不存在')
else:
    print('已关闭employees.csv的可视化')
#%%
if social_network == 1:
    visualize_library_path = 'Visualize Code Library'
    
    if os.path.exists(visualize_library_path):
        pattern = re.compile(r'.*people.*year.*\.csv')
        csv_files = [file for file in os.listdir(visualize_library_path) if pattern.match(file)]

        if csv_files:
            random_csv_file = random.choice(csv_files)
            csv_file_path = os.path.join(visualize_library_path, random_csv_file)
            with open(csv_file_path, 'r') as file:
                header = file.readline().strip()

            # 检查表头是否包含'max-friend' and 'max-min-friend'字段
            if 'max-friend' in header and 'min-friend' in header:
                process = subprocess.run(['python', os.path.join(visualize_library_path, 'social network.py')],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         text=True)

                print(process.stdout)

                if process.stderr:
                    print(process.stderr)

                print('已完成social network系列的可视化')
            else:
                print('people.csv字段不全，无friend相关字段')
        else:
            print('没有符合条件的people.csv文件')
    else:
        print('Visualize Code Library子文件夹不存在')
else:
    print('已关闭social_network的可视化')
#%%


visualize_library_path = 'Visualize Code Library'

if social_ave_friend == 1 and line == 1:
    if os.path.exists(visualize_library_path):
        pattern = re.compile(r'.*people.*year.*\.csv')
        csv_files = [file for file in os.listdir(visualize_library_path) if pattern.match(file)]

        if csv_files:
            random_csv_file = random.choice(csv_files)
            csv_file_path = os.path.join(visualize_library_path, random_csv_file)
            with open(csv_file_path, 'r') as file:
                header = file.readline().strip()

            # 检查表头是否包含'max-friend' and 'max-min-friend'字段
            if 'max-friend' in header and 'min-friend' in header:
                process = subprocess.run(['python', os.path.join(visualize_library_path, 'social ave friend.py')],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         text=True)

                print(process.stdout)

                if process.stderr:
                    print(process.stderr)

                print('已完成social_ave_friend折线图系列的可视化')
            else:
                print('people.csv字段不全，无friend相关字段')
        else:
            print('没有符合条件的people.csv文件')
    else:
        print('Visualize Code Library子文件夹不存在')
else:
    print('已关闭social_ave_friend或折线图line的可视化')

#%%
"""
"""

#%%
#清理visualize_code_library
def clean_visualize_code_library(folder_path):
    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)

                if not file.endswith('.py'):
                    os.remove(file_path)
                    print(f"")

        print("清理进行中")
    except Exception as e:
        print(f"{e}")


visualize_code_library_path = "Visualize Code Library"


clean_visualize_code_library(visualize_code_library_path)

def remove_folders_model(keyword, folder_path="."):
    try:
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                if keyword in item:
                    shutil.rmtree(item_path)
                    print("")

        print("清理完成")
    except Exception as e:
        print(f"{e}")

# 指定中转字段关键字
transit_transfer = "中转"

# 执行清理操作，默认在当前文件夹中
remove_folders_model(transit_transfer)
#%%
#格式整理
current_folder = os.getcwd()
for root, dirs, files in os.walk("."):
    for dir_name in dirs:
        source_path = os.path.join(root, dir_name)

        if GIF == 1 and "result" in dir_name:
            for sub_root, sub_dirs, sub_files in os.walk(source_path):
                for sub_file in sub_files:
                    source_file_path = os.path.join(sub_root, sub_file)
                    shutil.move(source_file_path, folder_name)

                for sub_dir in sub_dirs:
                    # 合并重复子文件夹的内容
                    sub_source_path = os.path.join(sub_root, sub_dir)
                    target_sub_path = os.path.join(folder_name, sub_dir)

                    if os.path.exists(target_sub_path):
                        for file_name in os.listdir(sub_source_path):
                            source_file_path = os.path.join(sub_source_path, file_name)
                            target_file_path = os.path.join(target_sub_path, file_name)
                            shutil.move(source_file_path, target_file_path)
                    else:
                        shutil.move(sub_source_path, folder_name)
        elif "result" in dir_name:
            # 移动带有 'result' 的文件夹到新文件夹
            shutil.move(source_path, os.path.join(folder_name, dir_name))
# 指定other字段关键字移动文件夹及其内容
current_directory = os.getcwd()
for directory in os.listdir(current_directory):
    if os.path.isdir(directory) and 'other' in directory:
        source_path = os.path.join(current_directory, directory)
        destination_path = os.path.join(current_directory, folder_name, directory)  # 更改 'new_location' 为您想要的目标位置
        shutil.move(source_path, destination_path)

# 指定中转字段关键字
transit_result = "result"

# 执行清理操作
remove_folders_model(transit_result)
#%%
csv_files = glob.glob("*year.csv")


for file in csv_files:
    shutil.move(file, folder_name)

print("文件移动完成！")

#%%
#GIF.py
current_folder = os.getcwd()

if GIF == 1:
    target_folders = ["Result output", "Result_output", "png_output"]
    target_file_found = False

    for folder in os.listdir():
        if os.path.isdir(folder) and any(target in folder for target in target_folders):
            target_file_found = True
            target_folder_path = folder
            break

    if target_file_found:
        shutil.copy(os.path.join("Visualize Code Library", "GIF.py"), current_folder)
        process = subprocess.run(['python', 'GIF.py'])
        os.remove(os.path.join(current_folder, 'GIF.py'))

        print("GIF生成已完成")
        current_directory = os.getcwd()
        original_path = os.path.join(current_directory, folder_name)
        

        new_folder_name = folder_name.replace("png_output_time", "GIF_finish")
        new_path = os.path.join(current_directory, new_folder_name)
        
        shutil.move(original_path, new_path)
        
        print(f"文件夹已成功更名为: {new_folder_name}")
    else:
        print("无目标文件")
else:
    print("GIF未开启")
#%%
final_check = "GIF.py"
if os.path.exists(final_check):
    os.remove(final_check)
    print("已完成全部过程")
else:
    print("已完成全部过程")