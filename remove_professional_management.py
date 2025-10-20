import os
from pymongo import MongoClient

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
apartments_collection = db['apartments']

print("=" * 60)
print("REMOVING 'Professional Management' FROM AMENITIES")
print("=" * 60)

# Find all apartments with "Professional Management" in amenities
apartments_with_pm = apartments_collection.count_documents({
    "amenities": "Professional Management"
})

print(f"\n📊 Found {apartments_with_pm} apartments with 'Professional Management' amenity")

if apartments_with_pm > 0:
    # Remove "Professional Management" from all amenities arrays
    result = apartments_collection.update_many(
        {"amenities": "Professional Management"},
        {"$pull": {"amenities": "Professional Management"}}
    )
    
    print(f"✅ Updated {result.modified_count} apartment listings")
    print(f"   Removed 'Professional Management' from amenities")
    
    # Verify removal
    remaining = apartments_collection.count_documents({
        "amenities": "Professional Management"
    })
    
    if remaining == 0:
        print(f"\n✅ SUCCESS: No apartments have 'Professional Management' amenity anymore")
    else:
        print(f"\n⚠️ WARNING: {remaining} apartments still have the amenity")
else:
    print("\n✅ No apartments found with 'Professional Management' amenity")

# Show a sample of updated apartments
print("\n" + "=" * 60)
print("SAMPLE OF UPDATED APARTMENTS:")
print("=" * 60)

sample_apartments = apartments_collection.find({}, {
    "title": 1, 
    "amenities": 1,
    "address": 1
}).limit(3)

for idx, apt in enumerate(sample_apartments, 1):
    print(f"\n{idx}. {apt['title']}")
    print(f"   Address: {apt['address']}")
    print(f"   Amenities count: {len(apt.get('amenities', []))}")
    if 'Professional Management' in apt.get('amenities', []):
        print(f"   ⚠️ Still has 'Professional Management'")
    else:
        print(f"   ✅ Clean (no 'Professional Management')")

total_count = apartments_collection.count_documents({})
print(f"\n📊 Total apartments in database: {total_count}")

client.close()
print("\n✅ Database operation completed!")
