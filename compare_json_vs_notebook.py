"""
Compare JSON Structure with Notebook Extraction
================================================
This script compares what's available in the JSON vs what the notebook extracts.
"""

print("="*80)
print("COMPARISON: JSON STRUCTURE vs NOTEBOOK EXTRACTION")
print("="*80)

print("""
📊 JSON STRUCTURE SUMMARY
========================

NODE TYPES (12 types):
  OBJECT_PAINTING: 5,839   ← Main entities
  ACTOR_PERSON: 2,772      ← Painters, commissioners, etc.
  OBJECT_ROOM: 2,376       ← Rooms containing paintings
  OBJECT_BUILDING: 1,260   ← Buildings
  TEXT: 1,230              ← Documents/descriptions
  FUNCTION: 200            ← Building/room functions
  ACTOR_SOCIETY: 59        ← Organizations
  OBJECT_ENSEMBLE: 32      ← Building complexes
  DATE: 21                 ← Date nodes
  LOCATION: 17             ← German states (Bundesländer)
  MATERIAL: 17             ← Materials (oil paint, etc.)
  METHOD: 12               ← Techniques (fresco, etc.)

NODE PROPERTIES:
  All nodes have: id, name, type
  Most have: val (numeric value for visualization)
  OBJECT_PAINTING: id, name, type (NO val)

LINK TYPES (33 types) - Key ones:
  From PAINTING (direct):
    ✅ PAINTERS: 3,595        → ACTOR_PERSON
    ✅ COMMISSIONERS: 4,962   → ACTOR_PERSON/SOCIETY  
    ✅ TEMPLATE_PROVIDERS: 1,006 → ACTOR_PERSON
    ✅ DESIGNERS: 306         → ACTOR_PERSON
    ✅ PLASTERERS: 197        → ACTOR_PERSON
    ✅ DATE: 7,373            → DATE nodes
    ✅ METHOD: 3,672          → METHOD nodes
    ✅ MATERIAL: 3,725        → MATERIAL nodes
    ⚠️ ARCHITECTS: 42         → ACTOR_PERSON (rare on paintings)
    ⚠️ ARTISTS: 86            → ACTOR_PERSON (generic)
    ⚠️ SCULPTORS: 11          → ACTOR_PERSON
    ⚠️ IMAGE_CARVERS: 13      → ACTOR_PERSON
    ⚠️ REFERENCE_PERSONS: 85  → ACTOR_PERSON
    
  From ROOM (linked via PART):
    ✅ ARCHITECTS: 869        → ACTOR_PERSON
    ✅ PLASTERERS: 599        → ACTOR_PERSON
    ✅ PAINTERS: 747          → ACTOR_PERSON
    ✅ COMMISSIONERS: 2,094   → ACTOR_PERSON
    ✅ FUNCTION: 1,601        → FUNCTION nodes
    ⚠️ SCULPTORS: 86          → ACTOR_PERSON
    ⚠️ DESIGNERS: 68          → ACTOR_PERSON
    
  From BUILDING:
    ✅ ARCHITECTS: 467        → ACTOR_PERSON
    ✅ COMMISSIONERS: 1,029   → ACTOR_PERSON
    ✅ FUNCTION: 1,220        → FUNCTION nodes
    ✅ LOCATION: 1,260        → LOCATION (Bundesland)
    ✅ DATE: 2,365            → DATE nodes
    ⚠️ PLASTERERS: 175        → ACTOR_PERSON
    ⚠️ PAINTERS: 358          → ACTOR_PERSON
    ⚠️ BUILDERS: 122          → ACTOR_PERSON
    ⚠️ SCULPTORS: 75          → ACTOR_PERSON
    ⚠️ OWNERS: 59             → ACTOR_PERSON/SOCIETY
    ⚠️ RESIDENTS: 57          → ACTOR_PERSON
    ⚠️ CONSTRUCTION_MANAGERS: 49 → ACTOR_PERSON
    ⚠️ LANDSCAPE_ARCHITECTS: 7 → ACTOR_PERSON
    
  PART Hierarchy:
    ✅ ROOM -> PAINTING: 5,753
    ✅ BUILDING -> ROOM: 2,323
    ✅ BUILDING -> PAINTING: 86 (direct)
    ✅ ENSEMBLE -> BUILDING: 61
    ✅ ROOM -> ROOM: 53 (nested rooms)

HIERARCHY PATTERNS (all 5,839 paintings reach a building!):
  PAINTING -> ROOM -> BUILDING: 5,114 (87.6%)
  PAINTING -> ROOM -> BUILDING -> ENSEMBLE: 437 (7.5%)
  PAINTING -> ROOM -> ROOM -> BUILDING: 121 (2.1%)
  PAINTING -> BUILDING (direct): 82 (1.4%)
  PAINTING -> ROOM -> ROOM -> BUILDING -> ENSEMBLE: 77 (1.3%)
  PAINTING -> BUILDING -> ENSEMBLE: 4
  PAINTING -> 5 ROOMS -> BUILDING: 4

""")

print("""
📋 NOTEBOOK EXTRACTION STATUS
=============================

✅ CURRENTLY EXTRACTING (in get_painting_relations):
  ✅ painters (PAINTERS link)
  ✅ commissioners (COMMISSIONERS link)
  ✅ architects (ARCHITECTS link) - from painting
  ✅ plasterers (PLASTERERS link)
  ✅ sculptors (SCULPTORS link)
  ✅ designers (DESIGNERS link)
  ✅ template_providers (TEMPLATE_PROVIDERS link)
  ✅ other_artists (ARTISTS, IMAGE_CARVERS, CABINETMAKERS, CARPENTERS)
  ✅ date (DATE link)
  ✅ method (METHOD link)
  ✅ material (MATERIAL link) - handled but not returned!
  
  Location hierarchy:
  ✅ room (via PART, traverse up)
  ✅ building (via traverse_to_building)
  ✅ building_function (FUNCTION from building)
  ✅ location_state (LOCATION from building)
  ✅ building_architects (ARCHITECTS from building)
  ✅ building_commissioners (COMMISSIONERS from building)

⚠️ MISSING OR INCOMPLETE:
  ❌ room_function - FUNCTION links on ROOM (1,601 links!)
  ❌ room_architects - ARCHITECTS on ROOM (869 links)
  ❌ room_plasterers - PLASTERERS on ROOM (599 links)  
  ❌ room_commissioners - COMMISSIONERS on ROOM (2,094 links)
  ❌ room_painters - PAINTERS on ROOM (747 links)
  ❌ ensemble - OBJECT_ENSEMBLE parent (32 ensembles, 61 buildings in them)
  ❌ building_builders - BUILDERS on BUILDING (122 links)
  ❌ building_sculptors - SCULPTORS on BUILDING (75 links)
  ❌ building_owners - OWNERS on BUILDING (59 links)
  ❌ building_residents - RESIDENTS on BUILDING (57 links)
  ❌ building_construction_date - DATE on BUILDING (2,365 links)
  ❌ reference_persons - REFERENCE_PERSONS link (255 total)
  ❌ donors - DONORS link (10 total)
  ❌ documents/text - TEXT nodes via DOCUMENTS link
  
  ACTOR_SOCIETY handling:
  ⚠️ COMMISSIONERS can be ACTOR_SOCIETY (183 from paintings)
  ⚠️ Current code only gets name, doesn't distinguish person/society

""")

print("""
🔧 RECOMMENDATIONS FOR NOTEBOOK UPDATE
======================================

1. ROOM DATA (high value - lots of data):
   - Add room_function (1,601 links available)
   - Add room_architects (869 links)
   - Add room_commissioners (2,094 links)
   - Add room_plasterers (599 links)

2. BUILDING DATA (medium value):
   - Add building_date (2,365 links - construction dates)
   - Add building_builders (122 links)
   - Add building_owners (59 links)

3. ENSEMBLE DATA (low volume but valuable):
   - Add ensemble name when building is part of one (61 buildings)
   - 437+ paintings are in ensembles

4. MATERIAL (currently parsed but not returned):
   - The code handles 'MATERIAL' link but doesn't add to result dict

5. Consider tracking link counts:
   - Some paintings have multiple painters (co-painters)
   - Some have multiple commissioners
   - Useful for network analysis

""")

print("✅ Comparison complete!")
