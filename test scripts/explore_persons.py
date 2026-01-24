from SPARQLWrapper import SPARQLWrapper, JSON
import requests

ENDPOINT_URL = 'https://nfdi4culture.de/sparql'
sparql = SPARQLWrapper(ENDPOINT_URL)
sparql.setReturnFormat(JSON)

# Get all person-related properties for a specific painting
query = """
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?prop ?gnd
WHERE {
  {
    <https://www.deckenmalerei.eu/fdb4a025-5a0c-43e3-b9c3-4ba6057f7017> <https://nfdi4culture.de/ontology/CTO_0001009> ?node .
    ?node <https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001006> ?gnd .
    BIND("CTO_0001009" AS ?prop)
  }
  UNION
  {
    <https://www.deckenmalerei.eu/fdb4a025-5a0c-43e3-b9c3-4ba6057f7017> <https://nfdi4culture.de/ontology/CTO_0001011> ?node .
    ?node <https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001006> ?gnd .
    BIND("CTO_0001011_Maler" AS ?prop)
  }
  UNION
  {
    <https://www.deckenmalerei.eu/fdb4a025-5a0c-43e3-b9c3-4ba6057f7017> <https://nfdi4culture.de/ontology/CTO_0001010> ?node .
    ?node <https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001006> ?gnd .
    BIND("CTO_0001010_Auftraggeber" AS ?prop)
  }
}
"""

sparql.setQuery(query)
results = sparql.query().convert()

print("Person-related properties for 'Divina Sapienza' painting:")
print("=" * 80)
for b in results['results']['bindings']:
    prop = b['prop']['value']
    gnd_uri = b['gnd']['value']
    gnd_id = gnd_uri.split('/')[-1]
    
    # Resolve GND to name
    try:
        resp = requests.get(f'https://lobid.org/gnd/{gnd_id}.json', timeout=10)
        if resp.ok:
            name = resp.json().get('preferredName', 'N/A')
        else:
            name = 'N/A'
    except:
        name = 'N/A'
    
    print(f"{prop:25} | {name:30} | {gnd_id}")

# Now check which paintings have CTO_0001011 (Maler) vs CTO_0001009
print("\n" + "=" * 80)
print("Checking data availability for Maler (CTO_0001011) vs generic (CTO_0001009)...")

query2 = """
PREFIX schema: <http://schema.org/>
PREFIX n4c: <https://nfdi4culture.de/id/>

SELECT 
  (COUNT(DISTINCT ?p1) AS ?with_CTO_0001009)
  (COUNT(DISTINCT ?p2) AS ?with_CTO_0001011_Maler)
  (COUNT(DISTINCT ?p3) AS ?with_CTO_0001010_Auftraggeber)
WHERE {
  n4c:E6077 schema:dataFeedElement ?feedItem .
  ?feedItem schema:item ?painting .
  
  OPTIONAL {
    ?painting <https://nfdi4culture.de/ontology/CTO_0001009> ?node1 .
    BIND(?painting AS ?p1)
  }
  OPTIONAL {
    ?painting <https://nfdi4culture.de/ontology/CTO_0001011> ?node2 .
    BIND(?painting AS ?p2)
  }
  OPTIONAL {
    ?painting <https://nfdi4culture.de/ontology/CTO_0001010> ?node3 .
    BIND(?painting AS ?p3)
  }
}
"""

sparql.setQuery(query2)
results2 = sparql.query().convert()
b = results2['results']['bindings'][0]
print(f"Paintings with CTO_0001009 (generic person): {b['with_CTO_0001009']['value']}")
print(f"Paintings with CTO_0001011 (Maler/painter): {b['with_CTO_0001011_Maler']['value']}")
print(f"Paintings with CTO_0001010 (Auftraggeber/commissioner): {b['with_CTO_0001010_Auftraggeber']['value']}")

# Check the node types for CTO_0001009
print("\n" + "=" * 80)
print("Checking node types for CTO_0001009...")

query3 = """
PREFIX schema: <http://schema.org/>
PREFIX n4c: <https://nfdi4culture.de/id/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?nodeType (COUNT(?node) AS ?count)
WHERE {
  n4c:E6077 schema:dataFeedElement ?feedItem .
  ?feedItem schema:item ?painting .
  ?painting <https://nfdi4culture.de/ontology/CTO_0001009> ?node .
  ?node rdf:type ?nodeType .
}
GROUP BY ?nodeType
ORDER BY DESC(?count)
"""

sparql.setQuery(query3)
results3 = sparql.query().convert()
for b in results3['results']['bindings']:
    node_type = b['nodeType']['value'].split('/')[-1]
    count = b['count']['value']
    print(f"  {node_type}: {count}")

# Get a painting that has BOTH CTO_0001011 and CTO_0001009 to compare
print("\n" + "=" * 80)
print("Sample painting with BOTH CTO_0001011 (Maler) and CTO_0001009...")

query4 = """
PREFIX schema: <http://schema.org/>
PREFIX n4c: <https://nfdi4culture.de/id/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?painting ?label ?malerGND ?genericGND
WHERE {
  n4c:E6077 schema:dataFeedElement ?feedItem .
  ?feedItem schema:item ?painting .
  ?painting rdfs:label ?label .
  ?painting <https://nfdi4culture.de/ontology/CTO_0001011> ?malerNode .
  ?malerNode <https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001006> ?malerGND .
  ?painting <https://nfdi4culture.de/ontology/CTO_0001009> ?genericNode .
  ?genericNode <https://nfdi.fiz-karlsruhe.de/ontology/NFDI_0001006> ?genericGND .
}
LIMIT 5
"""

sparql.setQuery(query4)
results4 = sparql.query().convert()
for b in results4['results']['bindings']:
    label = b['label']['value'][:40]
    maler = b['malerGND']['value'].split('/')[-1]
    generic = b['genericGND']['value'].split('/')[-1]
    print(f"  {label}")
    print(f"    Maler GND: {maler}")
    print(f"    Generic GND: {generic}")
    print()
