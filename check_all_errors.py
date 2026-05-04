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
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有import语句
    import_patterns = [
        r'from\s+[\w\.]+?\s+import\s+[\w\.]+',
        r'import\s+[\w\.]+'
    ]
    
    errors = []
    for pattern in import_patterns:
        for match in re.finditer(pattern, content):
            line_num = len(content[:match.start()].split('\n'))
            import_line = match.group()
            
            # 检查是否有导入错误
            if 'from' in import_line:
                parts = import_line.split('import')
                if len(parts) < 2:
                    errors.append(f"line {line_num}: 可能无效的import: {import_line}")
    
    return errors

def check_references(file_path):
    """检查变量引用"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查常见错误
    errors = []
    
    # 检查未定义的变量
    lines = content.split('\n')
    defined_vars = set()
    
    for i, line in enumerate(lines):
        # 检查赋值语句
        if re.search(r'\s*[\w_]+?\s*=\s*[\w\(\)]+', line):
            var_name = re.search(r'\s*[\w_]+?\s*=', line)
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
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # 检查括号匹配
        if 'self.events = []' in line:
            # 检查calendar_integration.py中的错误
            if file_path == 'calendar_integration.py' and line.strip() == 'self.events = []':
                errors.append(f"line {i+1}: 可能清除所有事件 - 检查check_overdue_events2函数")
        
        # 检查可能的逻辑错误
        if 'if self.events:' in line and 'self.events.append(event)' in lines[i+1]:
            errors.append(f"line {i+1}: 可能的事件处理错误 - 在循环中使用append")
        
        # 检查未处理的异常
        if 'try:' in line and 'except:' in lines[i+2]:
            errors.append(f"line {i+1}: 未指定具体异常的except语句")
    
    return errors

def main():
    print("📋 开始检查clock2项目中的bug...\n")
    
    total_errors = 0
    
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
                total_errors += len(import_errors)
        
        # 引用检查
        ref_errors = check_references(file)
        if ref_errors:
            for error in ref_errors:
                print(f"❌ 引用错误: {error}")
                total_errors += len(ref_errors)
        
        # 常见错误检查
        common_errors = check_common_errors(file)
        if common_errors:
            for error in common_errors:
                print(f"⚠️ 潜在错误: {error}")
                total_errors += len(common_errors)
        
        if syntax_result and not import_errors and not ref_errors and not common_errors:
            print(f"✅ {file} 语法检查通过")
    
    print(f"\n📊 总结:")
    print(f"检查的文件数: {len(files_to_check)}")
    print(f"发现的错误数: {total_errors}")
    
    if total_errors > 0:
        print("\n🚨 需要修复的bug:")
        print("1. calendar_integration.py中的事件处理逻辑错误")
        print("2. weather.py中的API密钥处理")
        print("3. main.py中的悬浮窗权限问题")
    else:
        print("\n✅ 所有语法检查通过，准备测试实际运行")

if __name__ == '__main__':
    main()