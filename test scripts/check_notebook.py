import json

# Read the notebook
with open(r'c:\Users\thano\Documents\_Studium\KIT\DataStories\DataStories\DataStory_Baroque.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

print('Notebook Structure Overview')
print('='*60)
cells = nb['cells']
print(f'Total cells: {len(cells)}')
print()

markdown_count = sum(1 for c in cells if c['cell_type'] == 'markdown')
code_count = sum(1 for c in cells if c['cell_type'] == 'code')

print(f'Markdown cells: {markdown_count}')
print(f'Code cells: {code_count}')
print()
print('All cells:')
for i, cell in enumerate(cells):
    ctype = cell['cell_type'][:4]
    src = ''.join(cell.get('source', []))[:55].replace('\n', ' ')
    print(f'{i:2}. [{ctype}] {src}...')
