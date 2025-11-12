#!/usr/bin/env python3
import asyncio
import aiohttp

async def check_building_data():
    base_url = 'https://auth-revamp-8.preview.emergentagent.com/api'
    unit_id = 'a56a07c7-d9a3-414d-95d8-104200f90351'
    
    async with aiohttp.ClientSession() as session:
        # Get the specific apartment
        async with session.get(f'{base_url}/apartments/{unit_id}') as response:
            if response.status == 200:
                data = await response.json()
                print('Unit 508 Data:')
                print(f'  ID: {data.get("id")}')
                print(f'  Title: {data.get("title")}')
                print(f'  Building ID: {data.get("building_id", "MISSING")}')
                print(f'  Building Name: {data.get("building_name", "MISSING")}')
                print(f'  Address: {data.get("address", "MISSING")}')
                print(f'  Price: {data.get("price")}')
                print(f'  Images: {len(data.get("images", []))}')
                print()
                
                # Search for Malt Drive apartments
                async with session.get(f'{base_url}/apartments?search=Malt Drive') as search_response:
                    if search_response.status == 200:
                        search_data = await search_response.json()
                        apartments = search_data.get('apartments', [])
                        print(f'Malt Drive Search Results: {len(apartments)} apartments')
                        for apt in apartments:
                            print(f'  - {apt.get("title", "No title")} - ${apt.get("price", 0)} - {apt.get("id", "No ID")}')
                        print()
                        
                        # Check if there's a building_id field in any apartment
                        building_ids = set()
                        for apt in apartments:
                            if 'building_id' in apt and apt['building_id']:
                                building_ids.add(apt['building_id'])
                        
                        print(f'Building IDs found: {building_ids}')
            else:
                print(f'Failed to get apartment: {response.status}')

asyncio.run(check_building_data())