import ast

files = ['main.py', 'resources.py', 'pet_mood.py', 'weather.py', 'calendar_integration.py']

for filepath in files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        print(f'{filepath}: OK')
    except SyntaxError as e:
        text = e.text.strip() if e.text else "<无法获取错误行内容>"
        print(f'{filepath}: SyntaxError at line {e.lineno}: {text}')
    except FileNotFoundError:
        print(f'{filepath}: File not found')
    except Exception as e:
        print(f'{filepath}: Error: {e}')
