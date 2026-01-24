import json

nb = json.load(open(r'c:\Users\thano\Documents\_Studium\KIT\DataStories\DataStories\DataStory_Baroque.ipynb', encoding='utf-8'))

print("Cells 20-30 with IDs:")
print("=" * 80)
for i, c in enumerate(nb['cells'][20:30]):
    idx = i + 20
    cell_id = c.get('id', '?')[:12]
    src = ''.join(c['source'])[:55].replace('\n', ' ')
    print(f"{idx}: {cell_id} | {src}")

print("\n\nCells 40-45 with IDs:")
print("=" * 80)
for i, c in enumerate(nb['cells'][40:45]):
    idx = i + 40
    cell_id = c.get('id', '?')[:12]
    src = ''.join(c['source'])[:55].replace('\n', ' ')
    print(f"{idx}: {cell_id} | {src}")
