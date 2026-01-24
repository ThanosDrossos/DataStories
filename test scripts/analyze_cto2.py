"""Analyze CTO fields for CbDD paintings."""

from SPARQLWrapper import SPARQLWrapper, JSON
import requests

ENDPOINT_URL = 'https://nfdi4culture.de/sparql'
sparql = SPARQLWrapper(ENDPOINT_URL)
sparql.setReturnFormat(JSON)

def resolve_gnd(uri):
    try:
        gnd_id = uri.split('/')[-1]
        resp = requests.get(f'https://lobid.org/gnd/{gnd_id}.json', timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('preferredName', '[Unknown]')
    except:
        pass
    gnd_id = uri.split('/')[-1]
    return f'[GND:{gnd_id}]'

# Get paintings from the CbDD feed using CTO_0001006
query = '''
PREFIX n4c: <https://nfdi4culture.de/id/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?painting ?label WHERE {
  ?painting <https://nfdi4culture.de/ontology/CTO_0001006> n4c:E6077 .
  ?painting rdfs:label ?label .
} LIMIT 5
'''
sparql.setQuery(query)
r = sparql.query().convert()
print('Paintings from CbDD feed (via CTO_0001006):')
paintings = []
for b in r.get('results', {}).get('bindings', []):
    uri = b.get('painting', {}).get('value', '')
    label = b.get('label', {}).get('value', '')
    paintings.append((uri, label))
    print(f'  {label[:50]}...')
    print(f'    URI: {uri}')

# Pick first painting and analyze all its CTO properties
if paintings:
    painting_uri, painting_label = paintings[0]
    print(f'\n\n{"="*70}')
    print(f'ANALYZING: {painting_label}')
    print(f'{"="*70}')
    
    # Get all CTO properties
    query2 = f'''
    SELECT ?prop ?val WHERE {{
      <{painting_uri}> ?prop ?val .
      FILTER(CONTAINS(STR(?prop), "CTO_"))
    }}
    ORDER BY ?prop
    '''
    sparql.setQuery(query2)
    r = sparql.query().convert()
    
    cto_props = {}
    for b in r.get('results', {}).get('bindings', []):
        prop = b.get('prop', {}).get('value', '').split('/')[-1]
        val = b.get('val', {}).get('value', '')
        if prop not in cto_props:
            cto_props[prop] = []
        cto_props[prop].append(val)
    
    print(f'\nCTO properties ({len(cto_props)} unique):')
    for prop, vals in sorted(cto_props.items()):
        print(f'\n  {prop}: ({len(vals)} values)')
        for v in vals[:3]:
            print(f'    -> {v}')
    
    # Now check CTO_0001011 (Maler) nodes
    print(f'\n\n{"="*70}')
    print('CTO_0001011 (Maler) NODE CONTENTS:')
    print(f'{"="*70}')
    
    query3 = f'''
    SELECT ?node ?pred ?val WHERE {{
      <{painting_uri}> <https://nfdi4culture.de/ontology/CTO_0001011> ?node .
      ?node ?pred ?val .
    }}
    '''
    sparql.setQuery(query3)
    r = sparql.query().convert()
    
    nodes = {}
    for b in r.get('results', {}).get('bindings', []):
        node = b.get('node', {}).get('value', '')
        pred = b.get('pred', {}).get('value', '').split('/')[-1]
        val = b.get('val', {}).get('value', '')
        if node not in nodes:
            nodes[node] = []
        nodes[node].append((pred, val))
    
    if not nodes:
        print('  (No CTO_0001011 nodes found)')
    else:
        for node, props in nodes.items():
            print(f'\nNode: ...{node[-40:]}')
            for pred, val in props:
                print(f'  {pred}: {val}')
                if 'NFDI_0001006' in pred and 'd-nb.info/gnd' in val:
                    name = resolve_gnd(val)
                    print(f'    -> RESOLVED: {name}')

    # Check CTO_0001010 (Commissioner) nodes
    print(f'\n\n{"="*70}')
    print('CTO_0001010 (Auftraggeber) NODE CONTENTS:')
    print(f'{"="*70}')
    
    query4 = f'''
    SELECT ?node ?pred ?val WHERE {{
      <{painting_uri}> <https://nfdi4culture.de/ontology/CTO_0001010> ?node .
      ?node ?pred ?val .
    }}
    '''
    sparql.setQuery(query4)
    r = sparql.query().convert()
    
    nodes = {}
    for b in r.get('results', {}).get('bindings', []):
        node = b.get('node', {}).get('value', '')
        pred = b.get('pred', {}).get('value', '').split('/')[-1]
        val = b.get('val', {}).get('value', '')
        if node not in nodes:
            nodes[node] = []
        nodes[node].append((pred, val))
    
    if not nodes:
        print('  (No CTO_0001010 nodes found)')
    else:
        for node, props in nodes.items():
            print(f'\nNode: ...{node[-40:]}')
            for pred, val in props:
                print(f'  {pred}: {val}')
                if 'NFDI_0001006' in pred and 'd-nb.info/gnd' in val:
                    name = resolve_gnd(val)
                    print(f'    -> RESOLVED: {name}')

    # Check CTO_0001009 (Person) nodes  
    print(f'\n\n{"="*70}')
    print('CTO_0001009 (Person) NODE CONTENTS:')
    print(f'{"="*70}')
    
    query5 = f'''
    SELECT ?node ?pred ?val WHERE {{
      <{painting_uri}> <https://nfdi4culture.de/ontology/CTO_0001009> ?node .
      ?node ?pred ?val .
    }}
    '''
    sparql.setQuery(query5)
    r = sparql.query().convert()
    
    nodes = {}
    for b in r.get('results', {}).get('bindings', []):
        node = b.get('node', {}).get('value', '')
        pred = b.get('pred', {}).get('value', '').split('/')[-1]
        val = b.get('val', {}).get('value', '')
        if node not in nodes:
            nodes[node] = []
        nodes[node].append((pred, val))
    
    if not nodes:
        print('  (No CTO_0001009 nodes found)')
    else:
        for node, props in nodes.items():
            print(f'\nNode: ...{node[-40:]}')
            for pred, val in props:
                print(f'  {pred}: {val}')
                if 'NFDI_0001006' in pred and 'd-nb.info/gnd' in val:
                    name = resolve_gnd(val)
                    print(f'    -> RESOLVED: {name}')

# Now let's sample multiple paintings with CTO_0001011 to see if they're all painters
print(f'\n\n{"="*70}')
print('VERIFYING CTO_0001011 = Maler (PAINTER)')
print('Sampling 10 paintings with CTO_0001011 and resolving GNDs:')
print(f'{"="*70}')

query6 = '''
PREFIX n4c: <https://nfdi4culture.de/id/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?painting ?label ?gnd WHERE {
  ?painting <https://nfdi4culture.de/ontology/CTO_0001006> n4c:E6077 .
  ?painting rdfs:label ?label .
  ?painting <https://nfdi4culture.de/ontology/CTO_0001011> ?node .
  ?node <https://nfdi4culture.de/ontology/NFDI_0001006> ?gnd .
} LIMIT 10
'''
sparql.setQuery(query6)
r = sparql.query().convert()

for b in r.get('results', {}).get('bindings', []):
    label = b.get('label', {}).get('value', '')[:40]
    gnd = b.get('gnd', {}).get('value', '')
    name = resolve_gnd(gnd)
    print(f'\n  Painting: {label}...')
    print(f'  CTO_0001011 GND: {gnd}')
    print(f'  -> RESOLVED: {name}')
