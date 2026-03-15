"""
检查所有 Python 文件中的 List 使用情况
找出使用了 List 但没有从 typing 导入的文件
"""
import os
import re

# 遍历所有 .py 文件
files_to_check = []
for root, dirs, files in os.walk("app"):
    for file in files:
        if file.endswith(".py"):
            files_to_check.append(os.path.join(root, file))

for file_path in sorted(files_to_check):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否使用了 List[（类型注解）
    if "List[" in content:
        # 检查是否导入了 List
        has_typing_import = False
        for line in content.split('\n')[:50]:  # 检查前 50 行
            if "from typing import" in line or "import typing" in line:
                has_typing_import = True
                break

        if not has_typing_import:
            print(f"⚠️  {file_path}: 使用了 List[ 但没有从 typing 导入")
