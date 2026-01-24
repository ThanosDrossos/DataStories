"""Compare query patterns for accessing CbDD paintings."""

from SPARQLWrapper import SPARQLWrapper, JSON

ENDPOINT_URL = 'https://nfdi4culture.de/sparql'
sparql = SPARQLWrapper(ENDPOINT_URL)
sparql.setReturnFormat(JSON)

# Check both query patterns
print('Test 1: Using schema:dataFeedElement (current notebook approach)')
query1 = '''
PREFIX n4c: <https://nfdi4culture.de/id/>
PREFIX schema: <http://schema.org/>
SELECT ?painting WHERE {
  n4c:E6077 schema:dataFeedElement ?feedItem .
  ?feedItem schema:item ?painting .
} LIMIT 3
'''
sparql.setQuery(query1)
r = sparql.query().convert()
count1 = len(r.get('results', {}).get('bindings', []))
print(f'  Results: {count1}')

print('\nTest 2: Using CTO_0001006 (discovered approach)')
query2 = '''
PREFIX n4c: <https://nfdi4culture.de/id/>
SELECT ?painting WHERE {
  ?painting <https://nfdi4culture.de/ontology/CTO_0001006> n4c:E6077 .
} LIMIT 3
'''
sparql.setQuery(query2)
r = sparql.query().convert()
count2 = len(r.get('results', {}).get('bindings', []))
print(f'  Results: {count2}')
for b in r.get('results', {}).get('bindings', []):
    print(f'    {b.get("painting", {}).get("value", "")}')

print('\nTest 3: What does n4c:E6077 schema:dataFeedElement link to?')
query3 = '''
PREFIX n4c: <https://nfdi4culture.de/id/>
PREFIX schema: <http://schema.org/>
SELECT ?o WHERE {
  n4c:E6077 schema:dataFeedElement ?o .
} LIMIT 5
'''
sparql.setQuery(query3)
r = sparql.query().convert()
bindings = r.get('results', {}).get('bindings', [])
print(f'  Results: {len(bindings)}')
for b in bindings[:3]:
    print(f'    {b.get("o", {}).get("value", "")}')

# Check the other approach used in the notebook
print('\nTest 4: CBDD_FEED_URI schema:dataFeedElement ?feedItem; ?feedItem schema:item ?painting')
query4 = '''
PREFIX n4c: <https://nfdi4culture.de/id/>
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?painting ?label WHERE {
  n4c:E6077 schema:dataFeedElement ?feedItem .
  ?feedItem schema:item ?painting .
  ?painting rdfs:label ?label .
} LIMIT 5
'''
sparql.setQuery(query4)
r = sparql.query().convert()
bindings = r.get('results', {}).get('bindings', [])
print(f'  Results: {len(bindings)}')
for b in bindings[:3]:
    print(f'    {b.get("label", {}).get("value", "")}')
