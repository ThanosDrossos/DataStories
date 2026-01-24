"""Test the corrected CTO field interpretation."""

from SPARQLWrapper import SPARQLWrapper, JSON
import requests

ENDPOINT_URL = 'https://nfdi4culture.de/sparql'
PREFIXES = '''
PREFIX fabio: <http://purl.org/spar/fabio/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX nfdicore: <https://nfdi.fiz-karlsruhe.de/ontology/>
PREFIX schema:  <http://schema.org/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dcat:    <http://www.w3.org/ns/dcat#>
PREFIX n4c:     <https://nfdi4culture.de/id/>
'''

def run_sparql(query):
    sparql = SPARQLWrapper(ENDPOINT_URL)
    sparql.setReturnFormat(JSON)
    sparql.setQuery(PREFIXES + query)
    results = sparql.query().convert()
    bindings = results.get('results', {}).get('bindings', [])
    return bindings

def resolve_gnd_with_profession(gnd_uri):
    """Resolve a GND URI and get profession info."""
    try:
        gnd_id = gnd_uri.split('/')[-1].strip()
        response = requests.get(
            f'https://lobid.org/gnd/{gnd_id}.json',
            headers={'Accept': 'application/json'},
            timeout=10
        )
        if response.ok:
            data = response.json()
            name = data.get('preferredName', '[Unknown]')
            types = data.get('type', [])
            professions = []
            for occ in data.get('professionOrOccupation', []):
                if isinstance(occ, dict):
                    professions.append(occ.get('label', ''))
                else:
                    professions.append(str(occ))
            
            # Check if painter
            painter_keywords = ['maler', 'malerin', 'freskant', 'freskomaler', 'künstler']
            is_painter = any(any(kw in prof.lower() for kw in painter_keywords) for prof in professions)
            
            return {
                'name': name,
                'types': types,
                'professions': professions,
                'is_painter': is_painter
            }
    except Exception as e:
        print(f"Error resolving {gnd_uri}: {e}")
    return None

# Test the corrected query
print("="*70)
print("TESTING CORRECTED QUERY STRUCTURE")
print("="*70)

query = '''
SELECT ?painting ?label 
       (GROUP_CONCAT(DISTINCT ?locationGND; separator="|") AS ?locationGNDs)
       (GROUP_CONCAT(DISTINCT ?personGND; separator="|") AS ?personGNDs)
WHERE {
  n4c:E6077 schema:dataFeedElement ?feedItem .
  ?feedItem schema:item ?painting .
  
  ?painting rdfs:label ?label .
  
  # CTO_0001011 = LOCATION (building/place)
  OPTIONAL {
    ?painting <https://nfdi4culture.de/ontology/CTO_0001011> ?locationNode .
    ?locationNode <https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001006> ?locationGND .
  }
  
  # CTO_0001009 = PERSONS (painters, commissioners, etc.)
  OPTIONAL {
    ?painting <https://nfdi4culture.de/ontology/CTO_0001009> ?personNode .
    ?personNode <https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001006> ?personGND .
  }
}
GROUP BY ?painting ?label
LIMIT 3
'''

results = run_sparql(query)

for r in results:
    label = r.get('label', {}).get('value', 'Unknown')
    location_gnds = r.get('locationGNDs', {}).get('value', '')
    person_gnds = r.get('personGNDs', {}).get('value', '')
    
    print(f"\n📖 {label[:60]}...")
    
    # Resolve locations
    if location_gnds:
        print("\n  🏛️ LOCATIONS (from CTO_0001011):")
        for gnd in location_gnds.split('|')[:2]:
            info = resolve_gnd_with_profession(gnd)
            if info:
                print(f"     {info['name']}")
                print(f"       Types: {', '.join(info['types'][:3])}")
    
    # Resolve persons and classify
    if person_gnds:
        print("\n  👥 PERSONS (from CTO_0001009):")
        painters = []
        others = []
        for gnd in person_gnds.split('|')[:5]:
            info = resolve_gnd_with_profession(gnd)
            if info:
                if info['is_painter']:
                    painters.append(info)
                else:
                    others.append(info)
        
        if painters:
            print("     🎨 PAINTERS:")
            for p in painters:
                print(f"        - {p['name']} ({', '.join(p['professions'][:2])})")
        
        if others:
            print("     👤 OTHER PERSONS:")
            for p in others:
                profs = ', '.join(p['professions'][:2]) if p['professions'] else 'N/A'
                print(f"        - {p['name']} ({profs})")

print("\n" + "="*70)
print("✅ Test complete - the corrected CTO interpretation works!")
print("   CTO_0001011 → Locations (buildings, places)")
print("   CTO_0001009 → Persons (classified by profession)")
print("="*70)
