import os
import json

def generate_py_json(folder_path, output_file):
    # 存储所有py文件的信息
    sites = []
    
    # 遍历文件夹及子目录
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 筛选出扩展名为py的文件
            if file.endswith('.py'):
                # 获取文件名（不含扩展名）
                file_name = os.path.splitext(file)[0]
                # 计算相对路径（相对于目标文件夹）
                relative_path2 = os.path.relpath(os.path.join(root, file), folder_path)
                relative_path = os.path.join(root, file)
                # 构建api路径（使用./开头）
                api_path = f'{relative_path.replace(os.sep, "/")}'  # 统一路径分隔符为/
                key_name = f'{relative_path2.replace(os.sep, "_")[:-3]}'
                PASS = False
                for i in black:
                    if i in f"py_{key_name}":
                        print(f"{api_path}已排除")
                        PASS = True
                        break
                if PASS:
                    continue
                # 生成单个py文件的JSON数据
                py_info = {
                    "key": f"py_{key_name}",
                    "name": f"{key_name}(py)",
                    "type": 3,
                    "api": api_path,
                    "searchable": 1,
                    "quickSearch": 1,
                    "filterable": 1,
                    "changeable": 1
                }
                sites.append(py_info)
    
    # 构建最终的JSON结构
    result = {"sites": sites}
    
    # 保存为JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    print(f"已生成JSON文件，共包含{len(sites)}个py文件信息")

# 使用示例
if __name__ == "__main__":
    black = ["小白调试示例","_adult_","分类筛选生成"]
    # 替换为你的目标文件夹路径
    target_folder = "./py"
    # 输出的JSON文件名
    output_json = "py_files_info.json"
    
    generate_py_json(target_folder, output_json)