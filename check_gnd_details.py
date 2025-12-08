"""Get detailed GND info to distinguish painters from commissioners."""

import requests
import json

def get_gnd_details(uri):
    try:
        gnd_id = uri.split('/')[-1]
        resp = requests.get(f'https://lobid.org/gnd/{gnd_id}.json', timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return {
                'name': data.get('preferredName', '[Unknown]'),
                'types': data.get('type', []),
                'professionOrOccupation': data.get('professionOrOccupation', []),
                'biographicalOrHistoricalInformation': data.get('biographicalOrHistoricalInformation', []),
            }
    except Exception as e:
        print(f'Error: {e}')
    return None

# Check the people from CTO_0001009
gnds = [
    'https://d-nb.info/gnd/118504606',   # Asam, Cosmas Damian
    'https://d-nb.info/gnd/118564420',   # Königsfeld
    'https://d-nb.info/gnd/118650580',   # Asam, Hans Georg
    'https://d-nb.info/gnd/1072103370',  # Asam, Maria Theresia
]

print('='*70)
print('DETAILED GND INFO FOR CTO_0001009 PERSONS')
print('='*70)

for gnd in gnds:
    details = get_gnd_details(gnd)
    if details:
        print(f"\nName: {details['name']}")
        print(f"GND: {gnd}")
        print(f"Types: {details['types']}")
        
        # Extract occupation labels
        occupations = []
        for occ in details['professionOrOccupation']:
            if isinstance(occ, dict):
                occupations.append(occ.get('label', str(occ)))
            else:
                occupations.append(str(occ))
        print(f"Professions: {occupations}")
        
        bio = details['biographicalOrHistoricalInformation']
        if bio:
            bio_text = bio[0] if isinstance(bio, list) else str(bio)
            print(f"Bio: {bio_text[:150]}...")
        print()

# Also check the location from CTO_0001011
print('='*70)
print('LOCATION FROM CTO_0001011')
print('='*70)
location_gnd = 'https://d-nb.info/gnd/127060371X'
details = get_gnd_details(location_gnd)
if details:
    print(f"Name: {details['name']}")
    print(f"Types: {details['types']}")
