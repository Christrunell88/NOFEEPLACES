#!/usr/bin/env python3
import requests
import json

print("🏢 GOTHAM WEST APARTMENTS API TESTING")
print("=" * 60)

# Test 1: Get all apartments
print("\n1. Testing GET /api/apartments (total count)")
response = requests.get('https://apartment-viewings.preview.emergentagent.com/api/apartments')
if response.status_code == 200:
    apartments = response.json()
    total_count = len(apartments)
    print(f'✅ Total apartments: {total_count}')
    
    # Count Gotham West apartments in full listing
    gotham_in_full = []
    for apt in apartments:
        title = apt.get('title', '').lower()
        if 'gotham' in title:
            gotham_in_full.append(apt)
    
    print(f'✅ Gotham West apartments in full listing: {len(gotham_in_full)}')
else:
    print(f'❌ Failed to get apartments: {response.status_code}')
    exit(1)

# Test 2: Search for Gotham West specifically
print("\n2. Testing search for 'Gotham West'")
search_response = requests.get('https://apartment-viewings.preview.emergentagent.com/api/apartments', params={'search_term': 'Gotham West'})
if search_response.status_code == 200:
    search_results = search_response.json()
    print(f'✅ Search for "Gotham West" returned: {len(search_results)} apartments')
    
    # Verify they are actually Gotham West apartments
    actual_gotham = []
    for apt in search_results:
        title = apt.get('title', '').lower()
        if 'gotham' in title:
            actual_gotham.append(apt)
    print(f'✅ Verified Gotham West apartments: {len(actual_gotham)}')
else:
    print(f'❌ Gotham West search failed: {search_response.status_code}')

# Test 3: Search for Hell's Kitchen
print("\n3. Testing search for 'Hell's Kitchen'")
hk_response = requests.get('https://apartment-viewings.preview.emergentagent.com/api/apartments', params={'search_term': "Hell's Kitchen"})
if hk_response.status_code == 200:
    hk_results = hk_response.json()
    hk_gotham_count = sum(1 for apt in hk_results if 'gotham' in apt.get('title', '').lower())
    print(f'✅ Search for "Hell\'s Kitchen" returned: {len(hk_results)} apartments')
    print(f'✅ Gotham West apartments in Hell\'s Kitchen search: {hk_gotham_count}')
else:
    print(f'❌ Hell\'s Kitchen search failed: {hk_response.status_code}')

# Test 4: Check apartment distribution
print("\n4. Testing apartment distribution (scattered throughout listings)")
if len(gotham_in_full) > 0:
    positions = []
    for i, apt in enumerate(apartments):
        if 'gotham' in apt.get('title', '').lower():
            positions.append(i + 1)
    
    if positions:
        min_pos = min(positions)
        max_pos = max(positions)
        spread = max_pos - min_pos
        print(f'✅ Gotham West positions: {positions}')
        print(f'✅ Distribution spread: positions {min_pos}-{max_pos} (spread: {spread})')
        
        # Check if well distributed (not all clustered)
        if spread > total_count * 0.2:  # Spread across at least 20% of listings
            print(f'✅ Good distribution - apartments are scattered')
        else:
            print(f'⚠️  Apartments may be clustered together')
    else:
        print(f'❌ No Gotham West apartments found for distribution check')

# Test 5: Check data structure
print("\n5. Testing apartment data structure")
if len(search_results) > 0:
    sample_apt = search_results[0]
    required_fields = ['id', 'title', 'address', 'price', 'bedrooms', 'bathrooms', 'sqft', 'neighborhood', 'borough', 'description', 'amenities', 'images', 'contact_info']
    
    missing_fields = []
    for field in required_fields:
        if field not in sample_apt:
            missing_fields.append(field)
    
    if not missing_fields:
        print(f'✅ All required fields present')
        print(f'✅ Sample apartment: {sample_apt.get("title")}')
        print(f'✅ Address: {sample_apt.get("address")}')
        print(f'✅ Price: ${sample_apt.get("price")}')
        print(f'✅ Neighborhood: {sample_apt.get("neighborhood")}')
        print(f'✅ Contact: {sample_apt.get("contact_info", {}).get("phone", "N/A")}')
    else:
        print(f'❌ Missing fields: {missing_fields}')

# Summary
print("\n" + "=" * 60)
print("📊 SUMMARY")
print("=" * 60)
print(f"Total apartments in database: {total_count}")
print(f"Gotham West apartments found: {len(gotham_in_full)}")
print(f"Gotham West search results: {len(search_results) if 'search_results' in locals() else 0}")
print(f"Hell's Kitchen search results: {len(hk_results) if 'hk_results' in locals() else 0}")
print(f"Gotham West in Hell's Kitchen: {hk_gotham_count if 'hk_gotham_count' in locals() else 0}")

# Check if requirements are met
requirements_met = []
requirements_met.append(("More apartments (should include Gotham West)", total_count >= 20))
requirements_met.append(("Gotham West search works", len(search_results) >= 5 if 'search_results' in locals() else False))
requirements_met.append(("Hell's Kitchen includes Gotham West", hk_gotham_count >= 3 if 'hk_gotham_count' in locals() else False))
requirements_met.append(("Apartments scattered", len(positions) > 1 and spread > 5 if 'positions' in locals() and positions else False))
requirements_met.append(("Proper data structure", len(missing_fields) == 0 if 'missing_fields' in locals() else False))

print(f"\n🎯 REQUIREMENTS CHECK:")
for req, met in requirements_met:
    status = "✅" if met else "❌"
    print(f"{status} {req}")

success_count = sum(1 for _, met in requirements_met if met)
total_reqs = len(requirements_met)
print(f"\n📈 Success Rate: {success_count}/{total_reqs} ({success_count/total_reqs*100:.1f}%)")