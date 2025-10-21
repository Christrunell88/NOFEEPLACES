import os
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('DB_NAME', 'nofeeplaces_database')

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
apartments_collection = db['apartments']

print("=" * 70)
print("MARKING BEST VALUE APARTMENTS")
print("=" * 70)

# Get apartments with price and sqft
apartments = list(apartments_collection.find({
    'price': {'$exists': True, '$gt': 0},
    'sqft': {'$exists': True, '$gt': 0},
    'amenities': {'$exists': True}
}))

# Premium and moderate neighborhoods for scoring
premium_neighborhoods = ['Financial District', 'Tribeca', 'SoHo', 'West Village', 
                        'Chelsea', 'Midtown', 'Upper West Side', 'Upper East Side',
                        'Williamsburg', 'DUMBO', 'Brooklyn Heights', 'Park Slope']

moderate_neighborhoods = ['Greenpoint', 'Murray Hill', 'Kips Bay', 'Gramercy',
                         'Fort Greene', 'Clinton Hill', 'Prospect Heights', 
                         'Bedford-Stuyvesant', 'Crown Heights']

# Calculate value scores
value_data = []

for apt in apartments:
    price_per_sqft = apt['price'] / apt['sqft']
    amenity_count = len(apt.get('amenities', []))
    
    # Neighborhood score
    neighborhood = apt.get('neighborhood', '')
    if any(n.lower() in neighborhood.lower() for n in premium_neighborhoods):
        neighborhood_score = 3
    elif any(n.lower() in neighborhood.lower() for n in moderate_neighborhoods):
        neighborhood_score = 2
    else:
        neighborhood_score = 1
    
    # Amenity score
    amenity_score = min(amenity_count / 5, 3)
    
    # Value score
    price_score = max(0, 3 - (price_per_sqft / 3))
    value_score = (price_score * 0.5) + (amenity_score * 0.3) + (neighborhood_score * 0.2)
    
    value_data.append({
        '_id': apt['_id'],
        'value_score': value_score,
        'price_per_sqft': price_per_sqft
    })

# Get top 20% threshold
all_scores = [v['value_score'] for v in value_data]
top_20_threshold = sorted(all_scores, reverse=True)[int(len(all_scores) * 0.2)]

print(f"\n📊 Value Score Threshold: {round(top_20_threshold, 2)}")

# First, set all apartments to best_value: False
apartments_collection.update_many({}, {'$set': {'best_value': False}})
print(f"✅ Reset all apartments to best_value=False")

# Mark top 20% as best value
best_value_ids = [v['_id'] for v in value_data if v['value_score'] >= top_20_threshold]

result = apartments_collection.update_many(
    {'_id': {'$in': best_value_ids}},
    {'$set': {
        'best_value': True,
        'updated_at': datetime.utcnow()
    }}
)

print(f"✅ Marked {result.modified_count} apartments as 'Best Value'")

# Show summary
best_value_apts = list(apartments_collection.find(
    {'best_value': True},
    {'title': 1, 'price': 1, 'sqft': 1, 'neighborhood': 1, 'building_name': 1}
).limit(10))

print(f"\n🏆 BEST VALUE APARTMENTS (Top 10):\n")
for i, apt in enumerate(best_value_apts, 1):
    sqft = apt.get('sqft', 0)
    price_per_sqft = round(apt['price'] / sqft, 2) if sqft > 0 else 0
    print(f"{i}. {apt.get('building_name', 'N/A')} - {apt.get('neighborhood', 'N/A')}")
    print(f"   ${apt['price']}/mo | {sqft} sqft | ${price_per_sqft}/sqft")

# Count by category
total_best_value = apartments_collection.count_documents({'best_value': True})
print(f"\n📊 Total Best Value Apartments: {total_best_value}")

client.close()
print("\n✅ Database update completed!")
