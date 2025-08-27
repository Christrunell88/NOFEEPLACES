#!/usr/bin/env python3
import requests
import json

# Get all apartments
response = requests.get('https://nyc-rental-platform.preview.emergentagent.com/api/apartments', params={'limit': 200})
if response.status_code == 200:
    apartments = response.json()
    print(f'Total apartments: {len(apartments)}')
    
    # Count Gotham West apartments
    gotham_apartments = []
    for apt in apartments:
        title = apt.get('title', '').lower()
        if 'gotham' in title:
            gotham_apartments.append(apt)
    
    print(f'Gotham West apartments found: {len(gotham_apartments)}')
    
    # Test search for Gotham West
    search_response = requests.get('https://nyc-rental-platform.preview.emergentagent.com/api/apartments', params={'search_term': 'Gotham West'})
    if search_response.status_code == 200:
        search_results = search_response.json()
        print(f'Search for "Gotham West" returned: {len(search_results)} apartments')
    
    # Test search for Hell's Kitchen
    hk_response = requests.get('https://nyc-rental-platform.preview.emergentagent.com/api/apartments', params={'search_term': "Hell's Kitchen"})
    if hk_response.status_code == 200:
        hk_results = hk_response.json()
        hk_gotham_count = sum(1 for apt in hk_results if 'gotham' in apt.get('title', '').lower())
        print(f'Search for "Hell\'s Kitchen" returned: {len(hk_results)} apartments, {hk_gotham_count} are Gotham West')
    
    # Check first few Gotham apartments for structure
    if gotham_apartments:
        print(f'\nFirst Gotham West apartment details:')
        apt = gotham_apartments[0]
        print(f'Title: {apt.get("title")}')
        print(f'Address: {apt.get("address")}')
        print(f'Price: ${apt.get("price")}')
        print(f'Neighborhood: {apt.get("neighborhood")}')
        print(f'Contact: {apt.get("contact_info")}')
        
        # Check if apartments are scattered
        print(f'\nGotham West apartment positions in full listing:')
        for i, apt in enumerate(apartments):
            if 'gotham' in apt.get('title', '').lower():
                print(f'Position {i+1}: {apt.get("title")}')
else:
    print(f'Failed to get apartments: {response.status_code}')