#!/usr/bin/env python3
"""
检查clock2项目中的所有语法错误和潜在bug
"""

import ast
import re
import os

# 要检查的文件列表
files_to_check = ['main.py', 'resources.py', 'pet_mood.py', 'weather.py', 'calendar_integration.py']

def check_syntax(file_path):
    """检查语法错误"""
    if not os.path.exists(file_path):
        return False, f"文件不存在: {file_path}"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"语法错误 at line {e.lineno}: {e.text}"
    except Exception as e:
        return False, f"错误: {e}"

def check_imports(file_path):
    """检查导入语句"""
    if not os.path.exists(file_path):
        return [f"文件不存在: {file_path}"]

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 查找所有import语句 - 贪婪匹配
    import_patterns = [
        r'from\s+[\w\.]+\s+import\s+[\w\.]+',
        r'import\s+[\w\.]+'
    ]

    errors = []
    for pattern in import_patterns:
        for match in re.finditer(pattern, content):
            line_num = len(content[:match.start()].split('\n'))
            import_line = match.group()

            # 检查是否有导入错误 - 修正 from x import y 验证逻辑
            if match.re.pattern.startswith('from'):
                # from xxx import yyy 格式检查
                parts = import_line.split('import')
                if len(parts) < 2 or not parts[1].strip():
                    errors.append(f"line {line_num}: 可能无效的import: {import_line}")
            else:
                # import xxx 格式检查
                parts = import_line.split('import')
                if len(parts) < 2 or not parts[1].strip():
                    errors.append(f"line {line_num}: 可能无效的import: {import_line}")

    return errors

def check_references(file_path):
    """检查变量引用"""
    if not os.path.exists(file_path):
        return [f"文件不存在: {file_path}"]

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查常见错误
    errors = []

    # 检查未定义的变量
    lines = content.split('\n')
    defined_vars = set()

    for i, line in enumerate(lines):
        # 检查赋值语句 - 贪婪匹配
        if re.search(r'\s*[\w_]+\s*=\s*[\w\(\)]+', line):
            var_name = re.search(r'\s*[\w_]+\s*=', line)
            if var_name:
                defined_vars.add(var_name.group().strip().replace('=', '').strip())

    # 检查变量使用
    for i, line in enumerate(lines):
        matches = re.findall(r'[\w_]+(?=\s*(\.|\[|=|\+|\-|\*|/|==|!=|<|>|and|or|in|not in))', line)
        for var in matches:
            if var not in defined_vars and not (var.startswith('self.') or var in ['True', 'False', 'None', 'print', 'import', 'from', 'def', 'class', 'if', 'else', 'elif', 'while', 'for', 'try', 'except', 'finally', 'return', 'break', 'continue', 'pass', 'raise', 'assert', 'global', 'nonlocal', 'yield', 'async', 'await']):
                errors.append(f"line {i+1}: 可能未定义的变量 '{var}'")

    return errors

def check_common_errors(file_path):
    """检查常见编程错误"""
    errors = []
    if not os.path.exists(file_path):
        return [f"文件不存在: {file_path}"]

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    total_lines = len(lines)
    for i, line in enumerate(lines):
        # 检查括号匹配
        if 'self.events = []' in line:
            # 检查calendar_integration.py中的错误
            if file_path == 'calendar_integration.py' and line.strip() == 'self.events = []':
                errors.append(f"line {i+1}: 可能清除所有事件 - 检查check_overdue_events2函数")

        # 检查可能的逻辑错误 - i+1 越界保护
        if 'if self.events:' in line and i + 1 < total_lines and 'self.events.append(event)' in lines[i+1]:
            errors.append(f"line {i+1}: 可能的事件处理错误 - 在循环中使用append")

        # 检查未处理的异常 - i+2 越界保护
        if 'try:' in line and i + 2 < total_lines and 'except:' in lines[i+2]:
            errors.append(f"line {i+1}: 未指定具体异常的except语句")

    return errors

def main():
    print("📋 开始检查clock2项目中的bug...\n")

    total_errors = 0
    import_total = 0
    ref_total = 0
    common_total = 0

    for file in files_to_check:
        print(f"\n🔍 检查文件: {file}")

        # 语法检查
        syntax_result, syntax_error = check_syntax(file)
        if not syntax_result:
            print(f"❌ 语法错误: {syntax_error}")
            total_errors += 1

        # 导入检查
        import_errors = check_imports(file)
        if import_errors:
            for error in import_errors:
                print(f"❌ 导入错误: {error}")
                total_errors += 1
            import_total += len(import_errors)

        # 引用检查
        ref_errors = check_references(file)
        if ref_errors:
            for error in ref_errors:
                print(f"❌ 引用错误: {error}")
                total_errors += 1
            ref_total += len(ref_errors)

        # 常见错误检查
        common_errors = check_common_errors(file)
        if common_errors:
            for error in common_errors:
                print(f"⚠️ 潜在错误: {error}")
                total_errors += 1
            common_total += len(common_errors)

        if syntax_result and not import_errors and not ref_errors and not common_errors:
            print(f"✅ {file} 语法检查通过")

    # 动态输出错误总结
    print(f"\n📊 总结:")
    print(f"检查的文件数: {len(files_to_check)}")
    print(f"发现的错误数: {total_errors}")

    if total_errors > 0:
        print("\n🚨 需要修复的bug:")
        if import_total > 0:
            print(f"- 导入语句错误: {import_total} 处")
        if ref_total > 0:
            print(f"- 变量引用错误: {ref_total} 处")
        if common_total > 0:
            print(f"- 潜在逻辑错误: {common_total} 处")
    else:
        print("\n✅ 所有语法检查通过，准备测试实际运行")

if __name__ == '__main__':
    main()
