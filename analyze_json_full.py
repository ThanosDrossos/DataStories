# =============================================================================
# Full JSON Structure Analysis Script
# =============================================================================
# This script analyzes graphData.json to extract:
# 1. All node types and their fields
# 2. All link types and their relationships
# 3. What data is available for enrichment

import json
from collections import defaultdict, Counter

# Load the JSON
with open('graphData.json', encoding='utf-8') as f:
    data = json.load(f)

print("="*80)
print("CBDD GRAPH DATA ANALYSIS")
print("="*80)

nodes = data['nodes']
links = data['links']

print(f"\nTotal nodes: {len(nodes)}")
print(f"Total links: {len(links)}")
print(f"Export date: {data.get('exportDate', 'unknown')}")

# =============================================================================
# 1. NODE TYPE ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("1. NODE TYPES AND THEIR FIELDS")
print("="*80)

# Group nodes by type
nodes_by_type = defaultdict(list)
for node in nodes:
    nodes_by_type[node.get('type', 'UNKNOWN')].append(node)

# Analyze each type
for node_type, type_nodes in sorted(nodes_by_type.items(), key=lambda x: -len(x[1])):
    print(f"\n{'='*60}")
    print(f"TYPE: {node_type} ({len(type_nodes)} nodes)")
    print("="*60)
    
    # Get all unique fields across nodes of this type
    all_fields = set()
    for node in type_nodes:
        all_fields.update(node.keys())
    
    print(f"Fields: {sorted(all_fields)}")
    
    # Sample node
    sample = type_nodes[0]
    print(f"\nSample node:")
    for key, value in sample.items():
        val_str = str(value)[:80] + "..." if len(str(value)) > 80 else str(value)
        print(f"  {key}: {val_str}")
    
    # Check if there are variations in fields
    field_counts = Counter()
    for node in type_nodes:
        for field in node.keys():
            field_counts[field] += 1
    
    # Fields that don't appear in all nodes
    partial_fields = {f: c for f, c in field_counts.items() if c < len(type_nodes)}
    if partial_fields:
        print(f"\nPartial fields (not in all nodes):")
        for field, count in partial_fields.items():
            print(f"  {field}: {count}/{len(type_nodes)} nodes")

# =============================================================================
# 2. LINK TYPE ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("2. LINK TYPES AND RELATIONSHIPS")
print("="*80)

# Group links by type
links_by_type = defaultdict(list)
for link in links:
    links_by_type[link['type']].append(link)

# Build node ID to type mapping for relationship analysis
node_id_to_type = {n['id']: n.get('type', 'UNKNOWN') for n in nodes}

# Analyze each link type
for link_type, type_links in sorted(links_by_type.items(), key=lambda x: -len(x[1])):
    print(f"\n{'='*60}")
    print(f"LINK TYPE: {link_type} ({len(type_links)} links)")
    print("="*60)
    
    # Analyze source -> target node type patterns
    patterns = Counter()
    for link in type_links:
        src_type = node_id_to_type.get(link['source'], 'UNKNOWN')
        tgt_type = node_id_to_type.get(link['target'], 'UNKNOWN')
        patterns[(src_type, tgt_type)] += 1
    
    print("Source -> Target patterns:")
    for (src, tgt), count in patterns.most_common(10):
        print(f"  {src} -> {tgt}: {count}")

# =============================================================================
# 3. PAINTING-SPECIFIC ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("3. PAINTING-SPECIFIC LINK ANALYSIS")
print("="*80)

paintings = [n for n in nodes if n.get('type') == 'OBJECT_PAINTING']
print(f"\nTotal paintings: {len(paintings)}")

# Build index
links_by_source = defaultdict(list)
links_by_target = defaultdict(list)
for link in links:
    links_by_source[link['source']].append(link)
    links_by_target[link['target']].append(link)

nodes_by_id = {n['id']: n for n in nodes}

# Count which link types paintings have as SOURCE
painting_outgoing_links = Counter()
for p in paintings:
    for link in links_by_source.get(p['id'], []):
        painting_outgoing_links[link['type']] += 1

print("\nOutgoing links FROM paintings (painting is source):")
for link_type, count in painting_outgoing_links.most_common():
    pct = 100 * count / len(paintings)
    print(f"  {link_type}: {count} ({pct:.1f}%)")

# Count which link types paintings have as TARGET
painting_incoming_links = Counter()
for p in paintings:
    for link in links_by_target.get(p['id'], []):
        painting_incoming_links[link['type']] += 1

print("\nIncoming links TO paintings (painting is target):")
for link_type, count in painting_incoming_links.most_common():
    pct = 100 * count / len(paintings)
    print(f"  {link_type}: {count} ({pct:.1f}%)")

# =============================================================================
# 4. ROOM-SPECIFIC ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("4. ROOM-SPECIFIC LINK ANALYSIS")
print("="*80)

rooms = [n for n in nodes if n.get('type') == 'OBJECT_ROOM']
print(f"\nTotal rooms: {len(rooms)}")

# Count which link types rooms have as SOURCE
room_outgoing_links = Counter()
for r in rooms:
    for link in links_by_source.get(r['id'], []):
        room_outgoing_links[link['type']] += 1

print("\nOutgoing links FROM rooms:")
for link_type, count in room_outgoing_links.most_common():
    pct = 100 * count / len(rooms)
    print(f"  {link_type}: {count} ({pct:.1f}%)")

# =============================================================================
# 5. BUILDING-SPECIFIC ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("5. BUILDING-SPECIFIC LINK ANALYSIS")
print("="*80)

buildings = [n for n in nodes if n.get('type') == 'OBJECT_BUILDING']
print(f"\nTotal buildings: {len(buildings)}")

# Count which link types buildings have as SOURCE
building_outgoing_links = Counter()
for b in buildings:
    for link in links_by_source.get(b['id'], []):
        building_outgoing_links[link['type']] += 1

print("\nOutgoing links FROM buildings:")
for link_type, count in building_outgoing_links.most_common():
    pct = 100 * count / len(buildings)
    print(f"  {link_type}: {count} ({pct:.1f}%)")

# =============================================================================
# 6. ALL LINK TYPES SUMMARY
# =============================================================================
print("\n" + "="*80)
print("6. ALL LINK TYPES SUMMARY")
print("="*80)

all_link_types = sorted(links_by_type.keys())
print(f"\nAll {len(all_link_types)} link types:")
for lt in all_link_types:
    print(f"  - {lt}: {len(links_by_type[lt])}")

# =============================================================================
# 7. PERSON-SPECIFIC ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("7. PERSON/ACTOR ANALYSIS")
print("="*80)

persons = [n for n in nodes if n.get('type') == 'ACTOR_PERSON']
print(f"\nTotal persons: {len(persons)}")

# What links do persons have?
person_incoming_links = Counter()
for p in persons:
    for link in links_by_target.get(p['id'], []):
        person_incoming_links[link['type']] += 1

print("\nIncoming links TO persons (person is target):")
for link_type, count in person_incoming_links.most_common():
    print(f"  {link_type}: {count}")

# =============================================================================
# 8. SPECIAL NODES ANALYSIS
# =============================================================================
print("\n" + "="*80)
print("8. SPECIAL NODE TYPES")
print("="*80)

# TEXT nodes
texts = [n for n in nodes if n.get('type') == 'TEXT']
print(f"\nTEXT nodes: {len(texts)}")
if texts:
    sample = texts[0]
    print(f"  Sample: {sample.get('name', '')[:100]}")

# FUNCTION nodes
functions = [n for n in nodes if n.get('type') == 'FUNCTION']
print(f"\nFUNCTION nodes: {len(functions)}")
if functions:
    func_names = [f.get('name', '') for f in functions[:10]]
    print(f"  Examples: {func_names}")

# ACTOR_SOCIETY nodes
societies = [n for n in nodes if n.get('type') == 'ACTOR_SOCIETY']
print(f"\nACTOR_SOCIETY nodes: {len(societies)}")
if societies:
    soc_names = [s.get('name', '') for s in societies[:5]]
    print(f"  Examples: {soc_names}")

# OBJECT_ENSEMBLE nodes
ensembles = [n for n in nodes if n.get('type') == 'OBJECT_ENSEMBLE']
print(f"\nOBJECT_ENSEMBLE nodes: {len(ensembles)}")
if ensembles:
    ens_names = [e.get('name', '') for e in ensembles[:5]]
    print(f"  Examples: {ens_names}")

# =============================================================================
# 9. EXTRACTION CHECKLIST
# =============================================================================
print("\n" + "="*80)
print("9. EXTRACTION CHECKLIST FOR NOTEBOOK")
print("="*80)

print("""
From PAINTINGS (outgoing links):
  ✓ PAINTERS -> ACTOR_PERSON (painters)
  ✓ COMMISSIONERS -> ACTOR_PERSON/ACTOR_SOCIETY (commissioners)
  ✓ ARCHITECTS -> ACTOR_PERSON (painting architects - rare)
  ✓ PLASTERERS -> ACTOR_PERSON (plasterers)
  ✓ SCULPTORS -> ACTOR_PERSON (sculptors)
  ✓ DESIGNERS -> ACTOR_PERSON (designers)
  ✓ TEMPLATE_PROVIDERS -> ACTOR_PERSON (template providers)
  ✓ DATE -> TEXT (creation date)
  ✓ METHOD -> TEXT (technique)
  ✓ MATERIAL -> TEXT (material)
  ? ARTISTS -> ACTOR_PERSON (generic artists)
  ? IMAGE_CARVERS -> ACTOR_PERSON (image carvers)
  ? CABINETMAKERS -> ACTOR_PERSON (cabinetmakers)
  ? CARPENTERS -> ACTOR_PERSON (carpenters)
  ? STUCCO_WORKERS -> ACTOR_PERSON (stucco workers)
  ? WOODCARVERS -> ACTOR_PERSON (woodcarvers)

From PAINTINGS (via PART hierarchy - painting is TARGET):
  ✓ PART: OBJECT_ROOM -> OBJECT_PAINTING (room contains painting)
  ✓ PART: OBJECT_BUILDING -> OBJECT_PAINTING (building contains painting directly)

From ROOMS (outgoing links):
  ✓ PART -> OBJECT_BUILDING (room is in building)
  ? COMMISSIONERS -> ACTOR_PERSON (room commissioners)
  ? ARCHITECTS -> ACTOR_PERSON (room architects)
  ? PLASTERERS -> ACTOR_PERSON (room plasterers)
  ? SCULPTORS -> ACTOR_PERSON (room sculptors)
  ? STUCCO_WORKERS -> ACTOR_PERSON (room stucco workers)
  ? FUNCTION -> FUNCTION (room function)
  ? DATE -> TEXT (room date)

From BUILDINGS (outgoing links):
  ✓ FUNCTION -> FUNCTION (building function)
  ✓ LOCATION -> TEXT (state/region)
  ✓ ARCHITECTS -> ACTOR_PERSON (building architects)
  ✓ COMMISSIONERS -> ACTOR_PERSON (building commissioners)
  ? BUILDERS -> ACTOR_PERSON (builders)
  ? DATE -> TEXT (construction date)
  ? PART -> OBJECT_ENSEMBLE (building is part of ensemble)
""")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
