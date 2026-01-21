"""
Analyze graphData.json Structure
================================
This script thoroughly analyzes the CbDD graph data to understand:
1. All node types and their properties
2. All link types and their relationships
3. What information is available for extraction
"""

import json
from collections import defaultdict, Counter
from pprint import pprint

# Load the graph data
print("Loading graphData.json...")
with open('graphData.json', encoding='utf-8') as f:
    graph = json.load(f)

print(f"Export Date: {graph.get('exportDate', 'unknown')}")
print(f"Total Nodes: {len(graph['nodes']):,}")
print(f"Total Links: {len(graph['links']):,}")

# =============================================================================
# PART 1: Analyze Node Structure
# =============================================================================
print("\n" + "="*80)
print("PART 1: NODE ANALYSIS")
print("="*80)

# Get all unique node types
node_types = Counter(n.get('type', 'UNKNOWN') for n in graph['nodes'])
print("\n📊 Node Types (count):")
for node_type, count in node_types.most_common():
    print(f"   {node_type}: {count:,}")

# Analyze properties for each node type
print("\n📋 Node Properties by Type:")
node_properties_by_type = defaultdict(lambda: defaultdict(int))
node_sample_by_type = {}

for node in graph['nodes']:
    node_type = node.get('type', 'UNKNOWN')
    for key in node.keys():
        node_properties_by_type[node_type][key] += 1
    
    # Keep a sample
    if node_type not in node_sample_by_type:
        node_sample_by_type[node_type] = node

for node_type in sorted(node_properties_by_type.keys()):
    props = node_properties_by_type[node_type]
    total = node_types[node_type]
    print(f"\n   {node_type} ({total} nodes):")
    for prop, count in sorted(props.items(), key=lambda x: -x[1]):
        pct = 100 * count / total
        print(f"      {prop}: {count} ({pct:.1f}%)")

# Show sample nodes for each type
print("\n📝 Sample Nodes by Type:")
for node_type, sample in sorted(node_sample_by_type.items()):
    print(f"\n   {node_type}:")
    for key, value in sample.items():
        val_str = str(value)[:80] + "..." if len(str(value)) > 80 else str(value)
        print(f"      {key}: {val_str}")

# =============================================================================
# PART 2: Analyze Link Structure
# =============================================================================
print("\n" + "="*80)
print("PART 2: LINK ANALYSIS")
print("="*80)

# Get all unique link types
link_types = Counter(l['type'] for l in graph['links'])
print("\n📊 Link Types (count):")
for link_type, count in link_types.most_common():
    print(f"   {link_type}: {count:,}")

# Analyze what node types each link connects
print("\n🔗 Link Type Relationships (source_type -> target_type):")
link_relationships = defaultdict(lambda: defaultdict(int))

nodes_by_id = {n['id']: n for n in graph['nodes']}

for link in graph['links']:
    link_type = link['type']
    source_node = nodes_by_id.get(link['source'], {})
    target_node = nodes_by_id.get(link['target'], {})
    source_type = source_node.get('type', 'UNKNOWN')
    target_type = target_node.get('type', 'UNKNOWN')
    
    relationship = f"{source_type} -> {target_type}"
    link_relationships[link_type][relationship] += 1

for link_type in sorted(link_relationships.keys()):
    relationships = link_relationships[link_type]
    total = link_types[link_type]
    print(f"\n   {link_type} ({total} total):")
    for rel, count in sorted(relationships.items(), key=lambda x: -x[1]):
        pct = 100 * count / total
        print(f"      {rel}: {count} ({pct:.1f}%)")

# =============================================================================
# PART 3: Analyze PART Hierarchy (critical for building lookup)
# =============================================================================
print("\n" + "="*80)
print("PART 3: PART HIERARCHY ANALYSIS")
print("="*80)

part_links = [l for l in graph['links'] if l['type'] == 'PART']
print(f"\n📊 Total PART links: {len(part_links):,}")

# Analyze PART hierarchy patterns
part_patterns = defaultdict(int)
links_by_target = defaultdict(list)
links_by_source = defaultdict(list)

for link in graph['links']:
    links_by_target[link['target']].append(link)
    links_by_source[link['source']].append(link)

def trace_hierarchy_up(node_id, depth=0, max_depth=10, path=None):
    """Trace from a node UP the PART hierarchy."""
    if depth >= max_depth:
        return path or []
    if path is None:
        path = []
    
    node = nodes_by_id.get(node_id)
    if not node:
        return path
    
    path.append(node.get('type', 'UNKNOWN'))
    
    # Find PART links where this node is the TARGET (i.e., find parents)
    parent_links = [l for l in links_by_target.get(node_id, []) if l['type'] == 'PART']
    
    if not parent_links:
        return path
    
    # Follow the first parent (there should typically be only one)
    parent_id = parent_links[0]['source']
    return trace_hierarchy_up(parent_id, depth + 1, max_depth, path)

# Trace hierarchy for all paintings
paintings = [n for n in graph['nodes'] if n.get('type') == 'OBJECT_PAINTING']
print(f"\n🎨 Tracing PART hierarchy for {len(paintings):,} paintings...")

painting_hierarchies = []
for painting in paintings:
    hierarchy = trace_hierarchy_up(painting['id'])
    painting_hierarchies.append(tuple(hierarchy))

hierarchy_patterns = Counter(painting_hierarchies)
print("\n📊 Painting Hierarchy Patterns (Painting -> Room -> Building etc.):")
for pattern, count in hierarchy_patterns.most_common(20):
    pattern_str = " -> ".join(pattern)
    print(f"   {pattern_str}: {count}")

# Check for paintings that DON'T reach a building
paintings_without_building = []
paintings_with_building = []
for painting, hierarchy in zip(paintings, painting_hierarchies):
    if 'OBJECT_BUILDING' in hierarchy:
        paintings_with_building.append((painting, hierarchy))
    else:
        paintings_without_building.append((painting, hierarchy))

print(f"\n📊 Building Coverage:")
print(f"   Paintings WITH building in hierarchy: {len(paintings_with_building):,}")
print(f"   Paintings WITHOUT building in hierarchy: {len(paintings_without_building):,}")

if paintings_without_building:
    print("\n⚠️ Sample paintings WITHOUT building:")
    for painting, hierarchy in paintings_without_building[:10]:
        print(f"   - {painting.get('name', 'Unknown')[:50]}")
        print(f"     Hierarchy: {' -> '.join(hierarchy)}")

# =============================================================================
# PART 4: Analyze Person/Actor Data
# =============================================================================
print("\n" + "="*80)
print("PART 4: ACTOR/PERSON ANALYSIS")
print("="*80)

persons = [n for n in graph['nodes'] if n.get('type') == 'ACTOR_PERSON']
societies = [n for n in graph['nodes'] if n.get('type') == 'ACTOR_SOCIETY']

print(f"\n📊 Actor Nodes:")
print(f"   ACTOR_PERSON: {len(persons):,}")
print(f"   ACTOR_SOCIETY: {len(societies):,}")

# Sample person properties
if persons:
    print("\n📝 Sample ACTOR_PERSON:")
    for key, value in persons[0].items():
        val_str = str(value)[:80] + "..." if len(str(value)) > 80 else str(value)
        print(f"   {key}: {val_str}")

# What links connect to persons?
person_link_types = defaultdict(int)
for link in graph['links']:
    target = nodes_by_id.get(link['target'], {})
    if target.get('type') == 'ACTOR_PERSON':
        person_link_types[link['type']] += 1

print("\n🔗 Link types pointing TO ACTOR_PERSON:")
for link_type, count in sorted(person_link_types.items(), key=lambda x: -x[1]):
    print(f"   {link_type}: {count:,}")

# =============================================================================
# PART 5: Analyze Building Data
# =============================================================================
print("\n" + "="*80)
print("PART 5: BUILDING ANALYSIS")
print("="*80)

buildings = [n for n in graph['nodes'] if n.get('type') == 'OBJECT_BUILDING']
print(f"\n📊 Total Buildings: {len(buildings):,}")

# Sample building properties
if buildings:
    print("\n📝 Sample OBJECT_BUILDING:")
    for key, value in buildings[0].items():
        val_str = str(value)[:80] + "..." if len(str(value)) > 80 else str(value)
        print(f"   {key}: {val_str}")

# What links go FROM buildings?
building_outgoing_links = defaultdict(int)
for link in graph['links']:
    source = nodes_by_id.get(link['source'], {})
    if source.get('type') == 'OBJECT_BUILDING':
        building_outgoing_links[link['type']] += 1

print("\n🔗 Link types FROM OBJECT_BUILDING:")
for link_type, count in sorted(building_outgoing_links.items(), key=lambda x: -x[1]):
    print(f"   {link_type}: {count:,}")

# What links go TO buildings?
building_incoming_links = defaultdict(int)
for link in graph['links']:
    target = nodes_by_id.get(link['target'], {})
    if target.get('type') == 'OBJECT_BUILDING':
        building_incoming_links[link['type']] += 1

print("\n🔗 Link types TO OBJECT_BUILDING:")
for link_type, count in sorted(building_incoming_links.items(), key=lambda x: -x[1]):
    print(f"   {link_type}: {count:,}")

# Check building name patterns (for address extraction)
print("\n📍 Building Name Patterns (sample):")
address_patterns = {
    'has_comma': 0,
    'has_street': 0,
    'has_number': 0,
}
import re
for building in buildings:
    name = building.get('name', '')
    if ',' in name:
        address_patterns['has_comma'] += 1
    if any(p in name.lower() for p in ['straße', 'str.', 'gasse', 'platz', 'weg', 'allee']):
        address_patterns['has_street'] += 1
    if re.search(r'\d+', name):
        address_patterns['has_number'] += 1

print(f"   Buildings with comma (City, Building): {address_patterns['has_comma']}/{len(buildings)}")
print(f"   Buildings with street keywords: {address_patterns['has_street']}/{len(buildings)}")
print(f"   Buildings with numbers: {address_patterns['has_number']}/{len(buildings)}")

print("\n📝 Sample Building Names:")
for building in buildings[:15]:
    print(f"   - {building.get('name', 'Unknown')}")

# =============================================================================
# PART 6: Analyze Function/Location Data
# =============================================================================
print("\n" + "="*80)
print("PART 6: FUNCTION AND LOCATION ANALYSIS")
print("="*80)

functions = [n for n in graph['nodes'] if n.get('type') == 'FUNCTION']
print(f"\n📊 FUNCTION Nodes: {len(functions):,}")

# Sample function values
print("\n📝 Sample FUNCTION values:")
function_names = [f.get('name', '') for f in functions]
for name in sorted(set(function_names))[:20]:
    count = function_names.count(name)
    print(f"   - {name}: {count}")

# LOCATION links analysis
location_links = [l for l in graph['links'] if l['type'] == 'LOCATION']
print(f"\n📊 LOCATION Links: {len(location_links):,}")

location_targets = Counter()
for link in location_links:
    target = nodes_by_id.get(link['target'], {})
    location_targets[target.get('name', 'Unknown')] += 1

print("\n📍 LOCATION Targets (states/regions):")
for loc, count in location_targets.most_common():
    print(f"   {loc}: {count}")

# =============================================================================
# PART 7: Other Node Types
# =============================================================================
print("\n" + "="*80)
print("PART 7: OTHER NODE TYPES")
print("="*80)

text_nodes = [n for n in graph['nodes'] if n.get('type') == 'TEXT']
ensemble_nodes = [n for n in graph['nodes'] if n.get('type') == 'OBJECT_ENSEMBLE']
room_nodes = [n for n in graph['nodes'] if n.get('type') == 'OBJECT_ROOM']

print(f"\n📊 TEXT Nodes: {len(text_nodes):,}")
if text_nodes:
    print("   Sample TEXT node:")
    for key, value in text_nodes[0].items():
        val_str = str(value)[:80] + "..." if len(str(value)) > 80 else str(value)
        print(f"      {key}: {val_str}")

print(f"\n📊 OBJECT_ENSEMBLE Nodes: {len(ensemble_nodes):,}")
if ensemble_nodes:
    print("   Sample OBJECT_ENSEMBLE names:")
    for e in ensemble_nodes[:10]:
        print(f"      - {e.get('name', 'Unknown')}")

print(f"\n📊 OBJECT_ROOM Nodes: {len(room_nodes):,}")
if room_nodes:
    print("   Sample OBJECT_ROOM names:")
    for r in room_nodes[:10]:
        print(f"      - {r.get('name', 'Unknown')}")

# =============================================================================
# PART 8: Summary - What Should Be Extracted
# =============================================================================
print("\n" + "="*80)
print("PART 8: SUMMARY - WHAT SHOULD BE EXTRACTED")
print("="*80)

print("""
📌 NODE TYPES TO EXTRACT:
   ✅ OBJECT_PAINTING - Main entities (paintings)
   ✅ OBJECT_ROOM - Rooms containing paintings
   ✅ OBJECT_BUILDING - Buildings containing rooms
   ✅ OBJECT_ENSEMBLE - Building complexes
   ✅ ACTOR_PERSON - Painters, commissioners, architects, etc.
   ✅ ACTOR_SOCIETY - Organizations/institutions
   ✅ FUNCTION - Building functions (church, palace, etc.)
   ✅ TEXT - Descriptions, dates, methods, materials

📌 LINK TYPES TO EXTRACT:
   From PAINTING:
""")

# List all link types that originate from paintings
painting_outgoing = defaultdict(int)
for link in graph['links']:
    source = nodes_by_id.get(link['source'], {})
    if source.get('type') == 'OBJECT_PAINTING':
        painting_outgoing[link['type']] += 1

for link_type, count in sorted(painting_outgoing.items(), key=lambda x: -x[1]):
    print(f"      {link_type}: {count:,}")

print("""
   From BUILDING:""")
for link_type, count in sorted(building_outgoing_links.items(), key=lambda x: -x[1]):
    print(f"      {link_type}: {count:,}")

print("""
   PART Hierarchy:
      PAINTING <- ROOM <- BUILDING <- ENSEMBLE (traced via _cbdd_links_by_target)
""")

print("\n✅ Analysis complete!")
