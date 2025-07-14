import os

old = 'App'
new = 'App'

for subdir, dirs, files in os.walk('.'):
    for filename in files:
        if filename.endswith('.py'):
            filepath = os.path.join(subdir, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            content = content.replace(f"'{old}'", f"'{new}'")
            content = content.replace(f'{old}.', f'{new}.')
            content = content.replace(f'from {old}', f'from {new}')
            content = content.replace(f'import {old}', f'import {new}')
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)
