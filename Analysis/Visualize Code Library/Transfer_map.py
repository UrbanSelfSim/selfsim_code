import os

parent_dir = os.path.dirname(os.path.abspath(__file__))
a_file_path = os.path.join(parent_dir, '..', 'Auto visualization.py')

with open(a_file_path, 'r', encoding='utf-8') as a_file:
    for line in a_file:
        if 'base_map_path' in line:
            base_map_path_line = line.strip()
            break

c_file_path = os.path.join(parent_dir, 'Base_Map.py')

with open(c_file_path, 'r', encoding='utf-8') as c_file:
    c_lines = c_file.readlines()

with open(c_file_path, 'w', encoding='utf-8') as c_file:
    for line in c_lines:
        if 'base_map_path' in line:
            c_file.write(base_map_path_line + '\n')
        else:
            c_file.write(line)
