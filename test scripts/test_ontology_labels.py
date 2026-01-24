"""Test the automatic ontology resolution functions."""

import requests
import re
import pandas as pd
from functools import lru_cache

# =============================================================================
# Ontology Sources (Raw TTL files from GitHub)
# =============================================================================
ONTOLOGY_SOURCES = {
    'CTO': {
        'url': 'https://raw.githubusercontent.com/ISE-FIZKarlsruhe/nfdi4culture/main/cto.ttl',
        'namespace': 'https://nfdi4culture.de/ontology/',
        'prefix_pattern': r'CTO_\d+',
    },
    'NFDIcore': {
        'url': 'https://raw.githubusercontent.com/ISE-FIZKarlsruhe/nfdicore/main/nfdicore.ttl',
        'namespace': 'https://nfdi.fiz-karlsruhe.de/ontology/',
        'prefix_pattern': r'NFDI_\d+',
    }
}

# Global cache for resolved ontology labels
_ontology_cache = {}
_ontology_loaded = False


def _parse_ttl_labels(ttl_content: str, namespace: str, prefix_pattern: str) -> dict:
    """
    Parse a TTL file and extract rdfs:label for entities matching the prefix pattern.
    Handles both full URI and prefix notation formats.
    """
    labels = {}
    
    # Pattern 1: Full URI format - <namespace/CODE> ... rdfs:label "Label"@en .
    entity_pattern = re.compile(
        rf'<{re.escape(namespace)}({prefix_pattern})>\s+[^;]*?'
        rf'rdfs:label\s+"([^"]+)"(?:@en)?\s*[;.]',
        re.MULTILINE | re.DOTALL
    )
    
    for match in entity_pattern.finditer(ttl_content):
        code = match.group(1)
        label = match.group(2)
        labels[code] = label
    
    # Pattern 2: Prefix notation - ontology:NFDI_XXXXXX ... rdfs:label "Label"@en
    # First find the prefix definition
    prefix_match = re.search(r'@prefix\s+(\w+):\s+<' + re.escape(namespace) + r'>\s*\.', ttl_content)
    if prefix_match:
        prefix_name = prefix_match.group(1)
        # Now find entities using that prefix
        prefix_entity_pattern = re.compile(
            rf'{prefix_name}:({prefix_pattern})\s+[^;]*?'
            rf'rdfs:label\s+"([^"]+)"(?:@en)?\s*[;.]',
            re.MULTILINE | re.DOTALL
        )
        for match in prefix_entity_pattern.finditer(ttl_content):
            code = match.group(1)
            label = match.group(2)
            if code not in labels:
                labels[code] = label
    
    # Pattern 3: Multi-line format with entity definition on one line, label on another
    lines = ttl_content.split('\n')
    current_entity = None
    
    for line in lines:
        # Check for full URI entity definition
        entity_match = re.match(rf'^<{re.escape(namespace)}({prefix_pattern})>', line)
        if entity_match:
            current_entity = entity_match.group(1)
        
        # Check for prefix notation entity definition (e.g., "ontology:NFDI_0000004")
        if prefix_match:
            prefix_name = prefix_match.group(1)
            prefix_entity_match = re.match(rf'^{prefix_name}:({prefix_pattern})\s', line)
            if prefix_entity_match:
                current_entity = prefix_entity_match.group(1)
        
        # Check for rdfs:label in the current context
        if current_entity:
            label_match = re.search(r'rdfs:label\s+"([^"]+)"(?:@en)?', line)
            if label_match and current_entity not in labels:
                labels[current_entity] = label_match.group(1)
            
            # Reset current entity on blank line or new entity definition
            if line.strip() == '':
                current_entity = None
    
    return labels


def load_ontology_labels(force_reload: bool = False) -> dict:
    """Load and cache all ontology labels from CTO and NFDIcore."""
    global _ontology_cache, _ontology_loaded
    
    if _ontology_loaded and not force_reload:
        return _ontology_cache
    
    print("📥 Loading ontology labels from GitHub...")
    
    for source_name, source_info in ONTOLOGY_SOURCES.items():
        try:
            print(f"   Fetching {source_name} from {source_info['url'][:50]}...")
            response = requests.get(source_info['url'], timeout=30)
            response.raise_for_status()
            
            labels = _parse_ttl_labels(
                response.text,
                source_info['namespace'],
                source_info['prefix_pattern']
            )
            
            for code, label in labels.items():
                _ontology_cache[code] = {
                    'label': label,
                    'namespace': source_info['namespace'],
                    'uri': f"{source_info['namespace']}{code}",
                    'source': source_name
                }
            
            print(f"   ✓ Loaded {len(labels)} labels from {source_name}")
            
        except Exception as e:
            print(f"   ⚠ Failed to load {source_name}: {e}")
    
    _ontology_loaded = True
    print(f"\n✅ Total: {len(_ontology_cache)} ontology codes resolved")
    return _ontology_cache


@lru_cache(maxsize=500)
def resolve_ontology_code(code: str) -> dict:
    """Resolve a CTO/NFDI ontology code to its label."""
    result = {'code': code, 'label': code, 'uri': None, 'source': None, 'resolved': False}
    
    # Ensure ontology is loaded
    if not _ontology_loaded:
        load_ontology_labels()
    
    if code in _ontology_cache:
        cached = _ontology_cache[code]
        result['label'] = cached['label']
        result['uri'] = cached['uri']
        result['source'] = cached['source']
        result['resolved'] = True
    else:
        # Construct URI even if label not found
        if code.startswith('CTO_'):
            result['uri'] = f"https://nfdi4culture.de/ontology/{code}"
            result['source'] = 'CTO'
        elif code.startswith('NFDI_'):
            result['uri'] = f"https://nfdi.fiz-karlsruhe.de/ontology/{code}"
            result['source'] = 'NFDIcore'
    
    return result


# =============================================================================
# Main test
# =============================================================================
if __name__ == '__main__':
    print("Testing Automatic Ontology Resolution")
    print("=" * 70)
    
    # Load ontology
    ontology_labels = load_ontology_labels()
    
    print("\n" + "=" * 70)
    print("Testing key CTO codes used in the CbDD dataset:")
    print("=" * 70)
    
    key_codes = [
        'CTO_0001005',  # Source Item
        'CTO_0001009',  # has related person
        'CTO_0001010',  # has subject concept
        'CTO_0001011',  # has related location
        'CTO_0001019',  # has subject concept (synonym?)
        'CTO_0001021',  # Creation date
        'CTO_0001026',  # related place literal
        'CTO_0001073',  # image URL
        'NFDI_0000003', # organization
        'NFDI_0000004', # person
        'NFDI_0000005', # place
        'NFDI_0001006', # has external identifier
    ]
    
    print()
    for code in key_codes:
        resolved = resolve_ontology_code(code)
        status = '✓' if resolved['resolved'] else '✗'
        print(f"  {status} {code:15} → {resolved['label']}")
    
    print("\n" + "=" * 70)
    print(f"Total codes in cache: {len(_ontology_cache)}")
    
    # Show first 20 CTO codes
    print("\nFirst 20 CTO codes:")
    cto_codes = sorted([k for k in _ontology_cache.keys() if k.startswith('CTO_')])
    for code in cto_codes[:20]:
        info = _ontology_cache[code]
        print(f"  {code}: {info['label']}")
    
    print("\nFirst 20 NFDI codes:")
    nfdi_codes = sorted([k for k in _ontology_cache.keys() if k.startswith('NFDI_')])
    for code in nfdi_codes[:20]:
        info = _ontology_cache[code]
        print(f"  {code}: {info['label']}")