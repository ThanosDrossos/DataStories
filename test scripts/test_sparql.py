"""Test SPARQL queries to ICONCLASS and Getty AAT endpoints."""
import requests

def test_iconclass():
    """Test ICONCLASS SPARQL endpoint."""
    query = '''
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    SELECT ?label WHERE {
        <https://iconclass.org/92D1521> skos:prefLabel ?label .
        FILTER(LANG(?label) = "en")
    } LIMIT 1
    '''
    resp = requests.get(
        'https://iconclass.org/sparql',
        params={'query': query, 'format': 'json'},
        headers={'Accept': 'application/sparql-results+json'},
        timeout=10
    )
    if resp.ok:
        data = resp.json()
        bindings = data.get('results', {}).get('bindings', [])
        if bindings:
            return bindings[0].get('label', {}).get('value')
    return None

def test_getty():
    """Test Getty AAT SPARQL endpoint."""
    query = '''
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?label WHERE {
        <http://vocab.getty.edu/aat/300004792> rdfs:label ?label .
        FILTER(LANG(?label) = "en")
    } LIMIT 1
    '''
    resp = requests.get(
        'http://vocab.getty.edu/sparql',
        params={'query': query, 'format': 'json'},
        headers={'Accept': 'application/sparql-results+json'},
        timeout=10
    )
    if resp.ok:
        data = resp.json()
        bindings = data.get('results', {}).get('bindings', [])
        if bindings:
            return bindings[0].get('label', {}).get('value')
    return None

if __name__ == '__main__':
    print("Testing SPARQL endpoints...")
    print("=" * 50)
    
    ic_label = test_iconclass()
    print(f"ICONCLASS 92D1521: {ic_label}")
    
    getty_label = test_getty()
    print(f"Getty AAT 300004792: {getty_label}")
    
    print("=" * 50)
    if ic_label and getty_label:
        print("✓ Both endpoints working!")
    else:
        print("✗ Some endpoints failed")
