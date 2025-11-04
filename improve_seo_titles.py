#!/usr/bin/env python3
"""
SEO Title Improvement Script
Optimizes apartment titles for better search engine visibility
"""
import os
from pymongo import MongoClient

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces_database')
client = MongoClient(MONGO_URL)
db = client["nofeeplaces_database"]

def generate_seo_title(apartment):
    """Generate SEO-optimized apartment title"""
    
    # Extract key details
    bedrooms = apartment.get('bedrooms', 0)
    bathrooms = apartment.get('bathrooms', 1)
    price = apartment.get('price', 0)
    building_name = (apartment.get('building_name') or '').strip()
    neighborhood = (apartment.get('neighborhood') or '').strip()
    borough = (apartment.get('borough') or 'NYC').strip()
    
    # Format bedroom/bathroom
    if bedrooms == 0:
        br_ba = f"Studio/{bathrooms}BA"
    else:
        br_ba = f"{bedrooms}BR/{bathrooms}BA"
    
    # Determine if it's a named building or generic
    is_named_building = building_name and building_name != 'Zillow Listings'
    
    # Build SEO-optimized title
    if is_named_building:
        # For named buildings: "No Fee 2BR/2BA at Chelsea Place | Chelsea, Manhattan NYC - $X,XXX"
        title = f"No Fee {br_ba} at {building_name} | {neighborhood}, {borough} NYC"
    else:
        # For generic listings: "No Fee 2BR/2BA Apartment in Chelsea, Manhattan NYC - $X,XXX"
        title = f"No Fee {br_ba} Apartment in {neighborhood}, {borough} NYC"
    
    # Add price range indicator for affordability searches
    if price < 2500:
        title += " - Affordable"
    elif price < 4000:
        title += " - Mid-Range"
    
    return title

def improve_all_titles():
    """Update all apartment titles with SEO-optimized versions"""
    
    print("=" * 70)
    print("SEO TITLE IMPROVEMENT")
    print("=" * 70)
    
    # Get all apartments
    apartments = list(db.apartments.find({}))
    
    print(f"\nFound {len(apartments)} apartments to update")
    print("\nProcessing...")
    
    updated_count = 0
    skipped_count = 0
    
    for apt in apartments:
        old_title = apt.get('title', '')
        new_title = generate_seo_title(apt)
        
        # Only update if title changed
        if old_title != new_title:
            db.apartments.update_one(
                {'id': apt['id']},
                {'$set': {'title': new_title}}
            )
            updated_count += 1
            
            if updated_count <= 5:  # Show first 5 examples
                print(f"\n✅ Updated:")
                print(f"   Old: {old_title}")
                print(f"   New: {new_title}")
        else:
            skipped_count += 1
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total apartments: {len(apartments)}")
    print(f"✅ Updated: {updated_count}")
    print(f"⏭️  Skipped (already optimized): {skipped_count}")
    print("\n✅ SEO title improvement complete!")

if __name__ == "__main__":
    improve_all_titles()
    client.close()
