"""Debug: Find paintings and analyze CTO fields."""

from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import requests
import sys

# Force output to be unbuffered
sys.stdout.reconfigure(line_buffering=True)

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
    try:
        sparql = SPARQLWrapper(ENDPOINT_URL)
        sparql.setReturnFormat(JSON)
        sparql.setQuery(PREFIXES + query)
        results = sparql.query().convert()
        bindings = results.get('results', {}).get('bindings', [])
        rows = []
        for binding in bindings:
            row = {var: val.get('value') for var, val in binding.items()}
            rows.append(row)
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"SPARQL Error: {e}")
        return pd.DataFrame()

def resolve_gnd(uri):
    """Resolve a GND URI to a name using lobid.org"""
    try:
        gnd_id = uri.split('/')[-1]
        resp = requests.get(f'https://lobid.org/gnd/{gnd_id}.json', timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('preferredName', f'[GND:{gnd_id}]')
    except:
        pass
    return f'[GND:{uri.split("/")[-1]}]'

# First, let's just find ANY painting from the feed
print("Step 1: Finding paintings from CbDD feed...")
test1 = '''
SELECT ?painting ?label WHERE {
  ?feedItem schema:about n4c:E6077 ;
            schema:dataFeedElement ?painting .
  ?painting rdfs:label ?label .
} LIMIT 3
'''
df1 = run_sparql(test1)
print(f"Found {len(df1)} paintings")
if not df1.empty:
    print(df1)

# If that fails, let's check the feed structure
print("\n\nStep 2: Check feed structure...")
test2 = '''
SELECT ?feedItem ?prop ?val WHERE {
  ?feedItem schema:about n4c:E6077 .
  ?feedItem ?prop ?val .
} LIMIT 20
'''
df2 = run_sparql(test2)
print(f"Feed properties: {len(df2)}")
if not df2.empty:
    print(df2)

# Let's also try to find all paintings with CTO_0001011
print("\n\nStep 3: Find paintings with CTO_0001011 (any method)...")
test3 = '''
SELECT ?painting ?label ?painterGND WHERE {
  ?painting <https://nfdi4culture.de/ontology/CTO_0001011> ?painterNode .
  ?painterNode <https://nfdi4culture.de/ontology/NFDI_0001006> ?painterGND .
  ?painting rdfs:label ?label .
} LIMIT 5
'''
df3 = run_sparql(test3)
print(f"Found {len(df3)} paintings with CTO_0001011")
if not df3.empty:
    print(df3)
    
    # Resolve the GND URIs
    print("\n\nResolving GND URIs from CTO_0001011:")
    for _, row in df3.iterrows():
        name = resolve_gnd(row['painterGND'])
        print(f"  {row['label'][:40]}...")
        print(f"    GND: {row['painterGND']}")
        print(f"    RESOLVED: {name}\n")

# Check what all CTO properties exist
print("\n\nStep 4: All CTO predicates in the dataset...")
test4 = '''
SELECT ?cto (COUNT(?s) as ?count)
WHERE {
  ?s ?cto ?o .
  FILTER(CONTAINS(STR(?cto), "CTO_"))
}
GROUP BY ?cto
ORDER BY DESC(?count)
LIMIT 30
'''
df4 = run_sparql(test4)
print("Most common CTO predicates:")
for _, row in df4.iterrows():
    cto_id = row['cto'].split('/')[-1]
    print(f"  {cto_id}: {row['count']} occurrences")
