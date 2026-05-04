import sys
import ast
import os

files = ['main.py', 'resources.py', 'pet_mood.py', 'weather.py', 'calendar_integration.py']

for file in files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        print(f'{file}: OK')
    except SyntaxError as e:
        print(f'{file}: SyntaxError at line {e.lineno}: {e.text}')
    except FileNotFoundError:
        print(f'{file}: File not found')
    except Exception as e:
        print(f'{file}: Error: {e}')