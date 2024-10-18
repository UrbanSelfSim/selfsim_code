import os
import shutil
from PIL import Image

#此代码应用于其他出图代码进行静态图片输出后，分类生成动图的过程
# 即将同文件夹中带有Result_output或Result output的文件夹进行分类，静图转动图。
#此代码为通用代码，即放置在其他出图代码的同一文件夹即可


current_directory = os.path.dirname(os.path.abspath(__file__))
#文件夹识别
#识别文件名含有"Result output文件"的文件
#matching_files = [file for file in os.listdir(current_directory) if "Result output" in file]
matching_files = [file for file in os.listdir(current_directory) if "Result output" in file or "Result_output" in file or "png_output" in file]

if matching_files:
    kinds_files = os.path.join(current_directory, matching_files[0])
else:
    kinds_files = None

print("kinds_files的路径为：", kinds_files)
#%%
current_folder = kinds_files
for file_name in os.listdir(current_folder):
    file_path = os.path.join(current_folder, file_name)
    if os.path.isdir(file_path):
        # 判断文件夹是否包含Equal Value子文件夹
        if "Equal Value" in file_name:
            eqv_folder = os.path.join(current_folder, file_name)
            for eqv_file_name in os.listdir(eqv_folder):
                eqv_file_path = os.path.join(eqv_folder, eqv_file_name)
                # 移动文件到文件夹外，并添加前缀
                new_file_name = "EqV" + eqv_file_name
                new_file_path = os.path.join(current_folder, new_file_name)
                shutil.move(eqv_file_path, new_file_path)
            # 删除Equal Value文件夹
            shutil.rmtree(eqv_folder)
        
        # 判断文件夹是否包含Geometrically Spaced子文件夹
        if "Geometrically Spaced" in file_name:
            gs_folder = os.path.join(current_folder, file_name)
            for gs_file_name in os.listdir(gs_folder):
                gs_file_path = os.path.join(gs_folder, gs_file_name)
                # 移动文件到文件夹外，并添加前缀
                new_file_name = "GS" + gs_file_name
                new_file_path = os.path.join(current_folder, new_file_name)
                shutil.move(gs_file_path, new_file_path)
            # 删除Geometrically Spaced文件夹
            shutil.rmtree(gs_folder)
#这一块代码是对EV部分的调整，使其可以适应EV部分
#%%

#文件夹分类

folder_path = kinds_files
csv_folder_path = os.path.join(folder_path, "csv")
os.makedirs(csv_folder_path, exist_ok=True)

# 移动csv文件到csv文件夹
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        csv_file_path = os.path.join(folder_path, filename)
        shutil.move(csv_file_path, os.path.join(csv_folder_path, filename))

# 提取图片文件名的文字部分
image_categories = set()

for filename in os.listdir(folder_path):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        #文字部分，忽略数字和扩展名
        name, _ = os.path.splitext(filename)
        category = ''.join(filter(str.isalpha, name))
        image_categories.add(category)

# 根据文字部分创建文件夹，并移动图片文件
for category in image_categories:
    category_folder_path = os.path.join(folder_path, category)
    os.makedirs(category_folder_path, exist_ok=True)
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            name, ext = os.path.splitext(filename)
            file_category = ''.join(filter(str.isalpha, name))
            if file_category == category:
                image_path = os.path.join(folder_path, filename)
                shutil.move(image_path, os.path.join(category_folder_path, filename))
                



def create_gif(folder_path):
    images = []
    folder_name = os.path.basename(folder_path)

    # 忽略包含"other"关键字的文件夹
    if "other" in folder_name.lower():
        print(f'Ignoring folder: {folder_name}')
        return

    image_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('jpg', 'jpeg', 'png', 'gif'))])

    for image_file in image_files:
        image_path = os.path.join(folder_path, image_file)
        img = Image.open(image_path).convert("RGB")
        images.append(img)

    # 生成动图
    gif_path = os.path.join(folder_path, f'{folder_name}.gif')
    images[0].save(gif_path, save_all=True, append_images=images[1:], loop=0, duration=500)

# 处理主文件夹中的子文件夹
main_folder = kinds_files  

for folder_name in os.listdir(main_folder):
    folder_path = os.path.join(main_folder, folder_name)
    if os.path.isdir(folder_path) and folder_name.lower() != 'csv':
        create_gif(folder_path)