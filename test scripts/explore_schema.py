from SPARQLWrapper import SPARQLWrapper, JSON

ENDPOINT_URL = 'https://nfdi4culture.de/sparql'
sparql = SPARQLWrapper(ENDPOINT_URL)
sparql.setReturnFormat(JSON)

# Find paintings with Maler (CTO_0001011) and explore the structure
query = """PREFIX schema: <http://schema.org/>
PREFIX n4c: <https://nfdi4culture.de/id/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX cto: <https://nfdi4culture.de/ontology/>

SELECT ?painting ?label ?malerGND ?auftragGND
WHERE {
  n4c:E6077 schema:dataFeedElement ?feedItem .
  ?feedItem schema:item ?painting .
  ?painting rdfs:label ?label .
  ?painting cto:CTO_0001011 ?maler .
  ?maler <https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001006> ?malerGND .
  OPTIONAL {
    ?painting cto:CTO_0001010 ?auftrag .
    ?auftrag <https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001006> ?auftragGND .
  }
}
LIMIT 10"""

sparql.setQuery(query)
results = sparql.query().convert()
print("Paintings with Maler (painter) and Auftraggeber (commissioner):")
print("="*70)
for b in results['results']['bindings']:
    label = b['label']['value']
    maler = b['malerGND']['value']
    auftrag = b.get('auftragGND', {}).get('value', 'N/A')
    print(f"\n{label}")
    print(f"  Maler (GND): {maler}")
    print(f"  Auftraggeber (GND): {auftrag}")

# Now let's explore the CTO_0001009 building node for a painting
print("\n\n" + "="*70)
print("Exploring CTO_0001009 (Building/Location) structure...")
print("="*70)

query2 = """PREFIX schema: <http://schema.org/>
PREFIX n4c: <https://nfdi4culture.de/id/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX cto: <https://nfdi4culture.de/ontology/>

SELECT ?buildingNode ?p ?o ?oLabel
WHERE {
  n4c:E6077 schema:dataFeedElement ?feedItem .
  ?feedItem schema:item ?painting .
  ?painting rdfs:label ?label .
  FILTER(CONTAINS(?label, "Divina Sapienza"))
  ?painting cto:CTO_0001009 ?buildingNode .
  ?buildingNode ?p ?o .
  OPTIONAL { ?o rdfs:label ?oLabel }
}
LIMIT 30"""

sparql.setQuery(query2)
results2 = sparql.query().convert()
for b in results2['results']['bindings']:
    pred = b['p']['value'].split('/')[-1]
    obj = b['o']['value'][:70]
    label = b.get('oLabel', {}).get('value', '')
    if label:
        print(f"{pred}: {label}")
    else:
        print(f"{pred}: {obj}")

# Explore the "ist Teil von" chain - find paintings that ARE part of something else
print("\n\n" + "="*70)
print("Exploring 'ist Teil von' chain via CTO_0001019...")
print("="*70)

# Find a painting that is part of something (not self-referential)
query3 = """PREFIX schema: <http://schema.org/>
PREFIX n4c: <https://nfdi4culture.de/id/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX cto: <https://nfdi4culture.de/ontology/>

SELECT ?painting ?paintingLabel ?parent ?parentLabel ?parentType
WHERE {
  n4c:E6077 schema:dataFeedElement ?feedItem .
  ?feedItem schema:item ?painting .
  ?painting rdfs:label ?paintingLabel .
  ?painting cto:CTO_0001019 ?parent .
  FILTER(?painting != ?parent)
  ?parent rdfs:label ?parentLabel .
  OPTIONAL { ?parent a ?parentType }
}
LIMIT 20"""

sparql.setQuery(query3)
results3 = sparql.query().convert()
print("\nPaintings with parent entities (ist Teil von):")
for b in results3['results']['bindings']:
    p_label = b['paintingLabel']['value']
    parent_label = b['parentLabel']['value']
    parent_type = b.get('parentType', {}).get('value', 'unknown').split('/')[-1]
    print(f"\n{p_label}")
    print(f"  -> ist Teil von: {parent_label} [{parent_type}]")

# Now let's trace up from a specific parent to find buildings with coordinates
if results3['results']['bindings']:
    parent_uri = results3['results']['bindings'][0]['parent']['value']
    print(f"\n\nExploring parent: {parent_uri}")
    
    query4 = f"""PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
PREFIX cto: <https://nfdi4culture.de/ontology/>

SELECT ?p ?o ?oLabel
WHERE {{
  <{parent_uri}> ?p ?o .
  OPTIONAL {{ ?o rdfs:label ?oLabel }}
}}
LIMIT 30"""
    
    sparql.setQuery(query4)
    results4 = sparql.query().convert()
    print("\nParent properties:")
    for b in results4['results']['bindings']:
        pred = b['p']['value'].split('/')[-1]
        obj = b['o']['value'][:60]
        label = b.get('oLabel', {}).get('value', '')
        if label:
            print(f"  {pred}: {label}")
        else:
            print(f"  {pred}: {obj}")
