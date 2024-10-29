import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

output_folder = "other social ave friend"
folder_path = "."
data_frames = []

for filename in os.listdir(folder_path):
    if filename.startswith("people") and filename.endswith("year.csv"):
        file_path = os.path.join(folder_path, filename)
        year = int(filename[6:10])  # 从文件名中提取年份
        df = pd.read_csv(file_path)
        data_frames.append((year, df))

average_friends_data = {'Year': [], 'Average Friends': []}


for year, df in data_frames:
    df['max-friend'] = df['max-friend'].astype(int)
    df['min-friend'] = df['min-friend'].astype(int)

    # 计算平均值并添加到数据框
    average_friends = df[['max-friend', 'min-friend']].mean().mean()
    average_friends_data['Year'].append(year)
    average_friends_data['Average Friends'].append(average_friends)

average_friends_df = pd.DataFrame(average_friends_data)

plt.plot(average_friends_df['Year'], average_friends_df['Average Friends'], marker='o', label='Average Friends', color='green', linewidth=2, linestyle='dotted')

plt.xlabel('Year')
plt.ylabel('Average Friends')
plt.xticks(average_friends_df['Year'], average_friends_df['Year'].tolist())
y_interval = 20  


y_min = average_friends_df['Average Friends'].min() - y_interval
y_max = average_friends_df['Average Friends'].max() + y_interval

ax = plt.gca()
ax.yaxis.set_major_locator(MultipleLocator(base=y_interval))
ax.set_ylim([y_min, y_max])
plt.tight_layout()
plt.legend(loc='upper center', fontsize=8, bbox_to_anchor=(0.5, -0.2), ncol=2)
plt.tight_layout(rect=(0, 0, 1, 0.9))
plt.ticklabel_format(style='plain', axis='y')
plt.xlim(average_friends_df['Year'].min() - 0.25, average_friends_df['Year'].max() + 0.25)
plt.grid()


output_folder = output_folder
os.makedirs(output_folder, exist_ok=True)


plt.savefig(os.path.join(output_folder, 'Average Friends Over the Years'))
plt.show()
