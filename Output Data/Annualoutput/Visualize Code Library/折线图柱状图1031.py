import csv
import re
import pandas as pd
import os
import numpy as np
import math
from datetime import datetime
file_path = "SelfSim - EV Social Demographic Attributes.csv"

#start_row表示第几行开始是数据
start_row = 32

#y_interval词条为y轴间隔，除了Householdlncome Population Change是自动调节，其他图因为多条线因此间隔是需要手动设置的
#索引从0开始，所以第28行在索引中是27,因此下面-1
start_row = start_row - 1
#x=0的开始年份
Year = 2018


data = pd.read_csv(file_path, skiprows=start_row)
data.to_csv('del_first.csv', index=True, encoding='utf-8')
first_file = 'del_first.csv'
second_file = 'del_second.csv'

with open(first_file, 'r', encoding='utf-8') as csvfile, open(second_file, 'w', encoding='utf-8', newline='') as output_csvfile:
    reader = csv.reader(csvfile)
    writer = csv.writer(output_csvfile)

    for row in reader:
        new_row = [data.strip('"') if isinstance(data, str) else data for data in row]
        writer.writerow(new_row)

data2 = pd.read_csv(second_file)
data2 = data2.rename(columns=lambda x: '' if 'Unnamed' in str(x) else x)
data2 = data2.replace("'", "")
#data2 = data2.dropna()


def round_and_remove_decimal(num):
    if isinstance(num, (int, float)) and not math.isnan(num):
        return round(num)
    else:
        return num

data2 = data2.round(0)
data2 = data2.applymap(round_and_remove_decimal)


data2.to_csv('del_second.csv', index=False)
def round_and_remove_decimal(num):
    if isinstance(num, str):

        num_parts = num.split('.')
        return num_parts[0]
    else:

        return num


data2 = data2.applymap(round_and_remove_decimal)

data2.to_csv('del_second.csv', index=False)

#%%
with open('del_second.csv', 'r') as file:
    reader = csv.reader(file)
    headers = next(reader)
    

    x_y_columns = []
    
    for row in reader:
        for i, cell in enumerate(row):
            if i < len(headers) and (cell == 'x' or cell == 'y'):
                x_y_columns.append(i)
        
with open('del_third.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    

    writer.writerow(headers)
    
    with open('del_second.csv', 'r') as file:
        reader = csv.reader(file)
        
        next(reader)
    
        for row in reader:
            new_row = [row[i] for i in x_y_columns]
            writer.writerow(new_row)

#%%
def read_csv_and_clean(filename):
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        data = list(csv_reader)
        
    header = [entry for entry in data[0] if entry != '']
    cleaned_data = data[1:]
    
    new_filename = 'del_fourth.csv'
    with open(new_filename, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(cleaned_data)
        
    return header

filename = 'del_third.csv'
type_table = read_csv_and_clean(filename)
print(type_table)
#print(new_filename)
#%%
data = pd.read_csv('del_fourth.csv')
columns = type_table
groups = []
output_folder = '输出分类'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for i in range(0, len(data.columns), 2):
    group = data.iloc[:, i:i+2]  
    group.columns = ['x', 'y'] 
    output_file_name = f"{type_table[i//2]}.csv"
    output_file = os.path.join(output_folder, output_file_name)
    group.to_csv(output_file, index=False)
    

file_names = [file for file in os.listdir(output_folder) if file.endswith('.csv')]

for file_name in file_names:
    file_path = os.path.join(output_folder, file_name)

    df = pd.read_csv(file_path)
    
    # 在"x"列中加入Year的值
    df['x'] = df['x'] + Year

    df.to_csv(file_path, index=False)
#%%
current_directory = os.getcwd()
files_and_folders = os.listdir(current_directory)

for item in files_and_folders:
    if item.startswith("del_") and item.endswith(".csv"):
        file_path = os.path.join(current_directory, item)
        os.remove(file_path)
#%%

#画图


import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
#Male Female
output_folder_line = '输出分类\折线图'
if not os.path.exists(output_folder_line):
    os.makedirs(output_folder_line)
output_folder_bar = '输出分类\柱状图'
if not os.path.exists(output_folder_bar):
    os.makedirs(output_folder_bar)

folder_path = '输出分类'

male_data = pd.read_csv(os.path.join(folder_path, 'Male.csv'))
female_data = pd.read_csv(os.path.join(folder_path, 'Female.csv'))

# 绘制折线图
plt.plot(male_data['x'], male_data['y'], label='Male',marker='o', color='blue',linewidth=2,linestyle='dotted')  
plt.plot(female_data['x'], female_data['y'], label='Female',marker='o', color='red',linewidth=2,linestyle='dotted')  

# 设置图的标签、标题等
plt.xlabel('Year')
plt.ylabel('Number')
plt.xticks(male_data['x'], male_data['x'].tolist())  
y_interval = 1000  # 设置你希望的y轴间隔

# 计算y轴的最小和最大值
y_min = min(male_data['y'].min(), female_data['y'].min()) - y_interval
y_max = max(male_data['y'].max(), female_data['y'].max()) + y_interval  

# 设置y轴刻度间隔和最小最大值
ax = plt.gca()
ax.yaxis.set_major_locator(MultipleLocator(base=y_interval))
ax.set_ylim([y_min, y_max])
plt.tight_layout()
plt.legend(loc='upper center', fontsize=8, bbox_to_anchor=(0.5, -0.2), ncol=2)
plt.tight_layout(rect=(0, 0, 1, 0.9))
plt.ticklabel_format(style='plain', axis='y')
plt.xlim(min(male_data['x'].min(), female_data['x'].min()) - 0.25, max(male_data['x'].max(), female_data['x'].max()) + 0.25)
plt.grid()
plt.savefig(os.path.join(output_folder_line, 'Gender Population Change'))
plt.show()

#柱状图
# 设置图的标签、标题等
plt.xlabel('Year')
plt.ylabel('Number')
plt.xticks(male_data['x'], male_data['x'].tolist())   

# 绘制多年柱状图
width = 0.35  # 柱状图的宽度
plt.bar(male_data['x'] - width/2, male_data['y'], width, label='Male',color='blue')  
plt.bar(female_data['x'] + width/2, female_data['y'], width, label='Female',color='red')  
plt.tight_layout()
plt.legend()

output_folder_bar = '输出分类\柱状图'
plt.savefig(os.path.join(output_folder_bar, 'Gender Population Change'))
plt.show()
#%%

students_data = pd.read_csv(os.path.join(folder_path, 'Students.csv'))
employee_data = pd.read_csv(os.path.join(folder_path, 'Employee.csv'))
retiree_data = pd.read_csv(os.path.join(folder_path, 'Retiree.csv'))
unemployee_data = pd.read_csv(os.path.join(folder_path, 'Unemployee.csv'))

# 绘制折线图
plt.plot(students_data['x'], students_data['y'], label='Students', marker='o', color='green', linewidth=2, linestyle='dotted')
plt.plot(employee_data['x'], employee_data['y'], label='Employee', marker='o', color='blue', linewidth=2, linestyle='dotted')
plt.plot(retiree_data['x'], retiree_data['y'], label='Retiree', marker='o', color='orange', linewidth=2, linestyle='dotted')
plt.plot(unemployee_data['x'], unemployee_data['y'], label='Unemployee', marker='o', color='red', linewidth=2, linestyle='dotted')

# 设置图的标签、标题等
plt.xlabel('Year')
plt.ylabel('Number')
plt.xticks(students_data['x'], students_data['x'].tolist())
y_interval = 2000  # 设置你希望的y轴间隔

# 计算y轴的最小和最大值
y_min = min(students_data['y'].min(), employee_data['y'].min(), retiree_data['y'].min(), unemployee_data['y'].min()) - y_interval
y_max = max(students_data['y'].max(), employee_data['y'].max(), retiree_data['y'].max(), unemployee_data['y'].max()) + y_interval

# 设置y轴刻度间隔和最小最大值
ax = plt.gca()
ax.yaxis.set_major_locator(MultipleLocator(base=y_interval))
ax.set_ylim([y_min, y_max])
plt.tight_layout()
plt.legend(loc='upper center', fontsize=8, bbox_to_anchor=(0.5, -0.2), ncol=4)
plt.tight_layout(rect=(0, 0, 1, 0.9))
plt.ticklabel_format(style='plain', axis='y')
plt.xlim(min(students_data['x'].min(), employee_data['x'].min(), retiree_data['x'].min(), unemployee_data['x'].min()) - 0.25,
         max(students_data['x'].max(), employee_data['x'].max(), retiree_data['x'].max(), unemployee_data['x'].max()) + 0.25)
plt.grid()
plt.savefig(os.path.join(output_folder_line, 'Work Population Change'))
plt.show()

# 柱状图
# 设置图的标签、标题等
plt.xlabel('Year')
plt.ylabel('Number')
plt.xticks(students_data['x'], students_data['x'].tolist())

# 绘制多年柱状图
width = 0.2  # 柱状图的宽度
plt.bar(students_data['x'] - width * 1.5, students_data['y'], width, label='Students', color='green')
plt.bar(employee_data['x'] - width / 2, employee_data['y'], width, label='Employee', color='blue')
plt.bar(retiree_data['x'] + width / 2, retiree_data['y'], width, label='Retiree', color='orange')
plt.bar(unemployee_data['x'] + width * 1.5, unemployee_data['y'], width, label='Unemployee', color='red')
plt.tight_layout()
plt.legend()

output_folder_bar = '输出分类\柱状图'
plt.savefig(os.path.join(output_folder_bar, 'Work Population Change'))
plt.show()

#%%
highschool_data = pd.read_csv(os.path.join(folder_path, 'Education-HighSchool or Below.csv'))
college_data = pd.read_csv(os.path.join(folder_path, 'Education-College.csv'))
bachelor_data = pd.read_csv(os.path.join(folder_path, 'Education-Bachelor.csv'))
master_phd_data = pd.read_csv(os.path.join(folder_path, 'Education-Master or PHD.csv'))

# 绘制折线图
plt.plot(highschool_data['x'], highschool_data['y'], label='HighSchool or Below', marker='o', color='blue', linewidth=2, linestyle='dotted')  
plt.plot(college_data['x'], college_data['y'], label='College', marker='o', color='red', linewidth=2, linestyle='dotted') 
plt.plot(bachelor_data['x'], bachelor_data['y'], label='Bachelor', marker='o', color='green', linewidth=2, linestyle='dotted') 
plt.plot(master_phd_data['x'], master_phd_data['y'], label='Master or PHD', marker='o', color='purple', linewidth=2, linestyle='dotted')  

# 设置图的标签、标题等
plt.xlabel('Year')
plt.ylabel('Number')
plt.xticks(highschool_data['x'], highschool_data['x'].tolist())  
y_interval = 1000  # 设置你希望的y轴间隔

# 计算y轴的最小和最大值
y_min = min(highschool_data['y'].min(), college_data['y'].min(), bachelor_data['y'].min(), master_phd_data['y'].min()) - y_interval
y_max = max(highschool_data['y'].max(), college_data['y'].max(), bachelor_data['y'].max(), master_phd_data['y'].max()) + y_interval  

# 设置y轴刻度间隔和最小最大值
ax = plt.gca()
ax.yaxis.set_major_locator(MultipleLocator(base=y_interval))
ax.set_ylim([y_min, y_max])
plt.tight_layout()
plt.legend(loc='upper center', fontsize=8, bbox_to_anchor=(0.5, -0.2), ncol=4)
plt.tight_layout(rect=(0, 0, 1, 0.9))
plt.ticklabel_format(style='plain', axis='y')
plt.xlim(min(highschool_data['x'].min(), college_data['x'].min(), bachelor_data['x'].min(), master_phd_data['x'].min()) - 0.25, max(highschool_data['x'].max(), college_data['x'].max(), bachelor_data['x'].max(), master_phd_data['x'].max()) + 0.25)
plt.grid()
plt.savefig(os.path.join(output_folder_line, 'Education Population Change'))
plt.show()

# 柱状图
# 设置图的标签、标题等
plt.xlabel('Year')
plt.ylabel('Number')
plt.xticks(highschool_data['x'], highschool_data['x'].tolist())   

# 绘制多年柱状图
width = 0.2  # 柱状图的宽度
plt.bar(highschool_data['x'] - 1.5*width, highschool_data['y'], width, label='HighSchool or Below', color='blue')  
plt.bar(college_data['x'] - 0.5*width, college_data['y'], width, label='College', color='red')  
plt.bar(bachelor_data['x'] + 0.5*width, bachelor_data['y'], width, label='Bachelor', color='green')  
plt.bar(master_phd_data['x'] + 1.5*width, master_phd_data['y'], width, label='Master or PHD', color='purple')  

plt.tight_layout()
plt.legend()

output_folder_bar = '输出分类\柱状图'
plt.savefig(os.path.join(output_folder_bar, 'Education Population Change'))
plt.show()
#%%
income_0_5k = pd.read_csv(os.path.join(folder_path, 'IndividualMonthlyIncome-0~5k.csv'))
income_5_10k = pd.read_csv(os.path.join(folder_path, 'IndividualMonthlyIncome-5~10k.csv'))
income_10_15k = pd.read_csv(os.path.join(folder_path, 'IndividualMonthlyIncome-10~15k.csv'))
income_15_20k = pd.read_csv(os.path.join(folder_path, 'IndividualMonthlyIncome-15~20k.csv'))
income_above_20k = pd.read_csv(os.path.join(folder_path, 'IndividualMonthlyIncome-Above20k.csv'))

# 绘制折线图
plt.plot(income_0_5k['x'], income_0_5k['y'], label='0~5k', marker='o', color='blue', linewidth=2, linestyle='dotted')
plt.plot(income_5_10k['x'], income_5_10k['y'], label='5~10k', marker='o', color='green', linewidth=2, linestyle='dotted')
plt.plot(income_10_15k['x'], income_10_15k['y'], label='10~15k', marker='o', color='orange', linewidth=2, linestyle='dotted')
plt.plot(income_15_20k['x'], income_15_20k['y'], label='15~20k', marker='o', color='red', linewidth=2, linestyle='dotted')
plt.plot(income_above_20k['x'], income_above_20k['y'], label='Above 20k', marker='o', color='purple', linewidth=2, linestyle='dotted')

# 设置图的标签、标题等
plt.xlabel('Year')
plt.ylabel('Number')
plt.xticks(income_0_5k['x'], income_0_5k['x'].tolist())
y_interval = 1000  # 设置你希望的y轴间隔

# 计算y轴的最小和最大值
y_min = min(income_0_5k['y'].min(), income_5_10k['y'].min(), income_10_15k['y'].min(), income_15_20k['y'].min(), income_above_20k['y'].min()) - y_interval
y_max = max(income_0_5k['y'].max(), income_5_10k['y'].max(), income_10_15k['y'].max(), income_15_20k['y'].max(), income_above_20k['y'].max()) + y_interval

# 设置y轴刻度间隔和最小最大值
ax = plt.gca()
ax.yaxis.set_major_locator(MultipleLocator(base=y_interval))
ax.set_ylim([y_min, y_max])
plt.tight_layout()
plt.legend(loc='upper center', fontsize=8, bbox_to_anchor=(0.5, -0.2), ncol=2)
plt.tight_layout(rect=(0, 0, 1, 0.9))
plt.ticklabel_format(style='plain', axis='y')
plt.xlim(min(income_0_5k['x'].min(), income_5_10k['x'].min(), income_10_15k['x'].min(), income_15_20k['x'].min(), income_above_20k['x'].min()) - 0.25, max(income_0_5k['x'].max(), income_5_10k['x'].max(), income_10_15k['x'].max(), income_15_20k['x'].max(), income_above_20k['x'].max()) + 0.25)
plt.grid()
plt.savefig(os.path.join(output_folder_line, 'Income Population Change'))
plt.show()

# 柱状图
# 设置图的标签、标题等
plt.xlabel('Year')
plt.ylabel('Number')
plt.xticks(income_0_5k['x'], income_0_5k['x'].tolist())

# 绘制多年柱状图
width = 0.15  # 柱状图的宽度
plt.bar(income_0_5k['x'] - 2*width, income_0_5k['y'], width, label='0~5k', color='blue')
plt.bar(income_5_10k['x'] - width, income_5_10k['y'], width, label='5~10k', color='green')
plt.bar(income_10_15k['x'], income_10_15k['y'], width, label='10~15k', color='orange')
plt.bar(income_15_20k['x'] + width, income_15_20k['y'], width, label='15~20k', color='red')
plt.bar(income_above_20k['x'] + 2*width, income_above_20k['y'], width, label='Above 20k', color='purple')
plt.tight_layout()
plt.legend()

output_folder_bar = '输出分类\柱状图'
plt.savefig(os.path.join(output_folder_bar, 'Income Population Change'))
plt.show()

#%%

Householdlncome_data = pd.read_csv(os.path.join(folder_path, 'HouseholdIncome.csv'))

# 绘制折线图
plt.plot(Householdlncome_data['x'], Householdlncome_data['y'], label='Householdlncome',marker='o', color='blue',linewidth=2,linestyle='dotted')  

# 设置图的标签、标题等
plt.xlabel('Year')
plt.ylabel('Number')
plt.xticks(Householdlncome_data['x'], Householdlncome_data['x'].tolist())  
y_interval = 1000  # 设置你希望的y轴间隔

# 计算y轴的最小和最大值
y_min = min(Householdlncome_data['y'])
y_max = max(Householdlncome_data['y'])
num_ticks = 7  # 想有几个
y_interval = (y_max - y_min) / num_ticks
y_min = int(min(Householdlncome_data['y']- y_interval/2))
y_max = int(max(Householdlncome_data['y']+ y_interval/2))
# 设置y轴刻度间隔和最小最大值
ax = plt.gca()
ax.yaxis.set_major_locator(MultipleLocator(base=y_interval))
ax.set_ylim([y_min, y_max])
plt.tight_layout()
plt.legend(loc='upper center', fontsize=8, bbox_to_anchor=(0.5, -0.2), ncol=2)
plt.tight_layout(rect=(0, 0, 1, 0.9))
plt.ticklabel_format(style='plain', axis='y')
plt.xlim(min(Householdlncome_data['x']) - 0.25, max(Householdlncome_data['x']) + 0.25)
plt.grid()
plt.savefig(os.path.join(output_folder_line, 'Householdlncome Population Change'))
plt.show()
#柱状图
# 设置图的标签、标题等
plt.xlabel('Year')
plt.ylabel('Number')
plt.xticks(Householdlncome_data['x'], Householdlncome_data['x'].tolist())   
# 绘制多年柱状图
width = 0.35  # 柱状图的宽度
plt.bar(Householdlncome_data['x'] - width/2, Householdlncome_data['y'], width, label='Householdlncome',color='blue')  
plt.tight_layout()
plt.legend()
output_folder_bar = '输出分类\柱状图'
plt.savefig(os.path.join(output_folder_bar, 'Householdlncome Population Change'))
plt.show()
#%%
People_data = pd.read_csv(os.path.join(folder_path, 'People.csv'))

# 绘制折线图
plt.plot(People_data['x'], People_data['y'], label='People',marker='o', color='blue',linewidth=2,linestyle='dotted')  

# 设置图的标签、标题等
plt.xlabel('Year')
plt.ylabel('Number')
plt.xticks(People_data['x'], People_data['x'].tolist())  
#y_interval = 500  # 设置你希望的y轴间隔
y_min = min(People_data['y'])
y_max = max(People_data['y'])
num_ticks = 5  # 想有几个
y_interval = (y_max - y_min) / num_ticks
y_min = int(min(People_data['y'] - y_interval/2))
y_max = int(max(People_data['y']+ y_interval/2))


# 设置y轴刻度间隔和最小最大值
ax = plt.gca()
ax.yaxis.set_major_locator(MultipleLocator(base=y_interval))
ax.set_ylim([y_min, y_max])
plt.tight_layout()
plt.legend(loc='upper center', fontsize=8, bbox_to_anchor=(0.5, -0.2), ncol=2)
plt.tight_layout(rect=(0, 0, 1, 0.9))
plt.ticklabel_format(style='plain', axis='y')
plt.xlim(min(People_data['x']) - 0.25, max(People_data['x']) + 0.25)
plt.grid()
plt.savefig(os.path.join(output_folder_line, 'People Population Change'))
plt.show()
#柱状图
# 设置图的标签、标题等
plt.xlabel('Year')
plt.ylabel('Number')
plt.xticks(People_data['x'], People_data['x'].tolist())   
# 绘制多年柱状图
width = 0.35  # 柱状图的宽度
plt.bar(People_data['x'] - width/2, People_data['y'], width, label='People',color='blue')  
plt.tight_layout()
plt.legend()
output_folder_bar = '输出分类\柱状图'
plt.savefig(os.path.join(output_folder_bar, 'People Population Change'))
plt.show()

#%%
current_time = datetime.now()
old_name = '输出分类'
new_name = "输出分类" + current_time.strftime("%Y-%m-%d-%H-%M-%S")
os.rename(old_name, new_name)

