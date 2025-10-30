# Building-Centric Database Organization

## Overview

The database has been reorganized into a hierarchical structure: **Buildings → Units**. This makes it much easier to:
- Identify where each listing belongs
- Add new units to existing buildings
- Manage building-level data (amenities, location, etc.)
- Avoid duplicate buildings

---

## New Database Structure

### Collections

**1. `buildings` Collection**
```json
{
  "building_id": "uuid",
  "building_name": "Chelsea Place®",
  "address": "363 West 30th Street, New York, NY 10001",
  "neighborhood": "Chelsea",
  "borough": "Manhattan",
  "amenities": ["Elevator", "Gym", "Doorman", ...],
  "images": ["exterior1.jpg", "exterior2.jpg"],
  "total_units": 2,
  "available_units": 2,
  "price_range": {
    "min": 4400,
    "max": 7050,
    "avg": 5725
  },
  "bedroom_types": [1, 2],
  "created_at": "2025-01-30T...",
  "updated_at": "2025-01-30T..."
}
```

**2. `apartments` Collection (Updated)**
```json
{
  "id": "uuid",
  "building_id": "reference-to-building",
  "building_name": "Chelsea Place®",
  "unit_number": "E1YXVQTJ",
  "title": "Beautiful 1BR at Chelsea Place®",
  "price": 4400,
  "bedrooms": 1,
  "bathrooms": 1,
  "sqft": 650,
  "images": ["unit_interior1.jpg", ...],
  "amenities": [...],
  "address": "363 West 30th Street, New York, NY 10001",
  "available": true,
  ...
}
```

---

## Scripts

### 1. Reorganization Script

**File:** `/app/reorganize_by_building.py`

**Purpose:** Migrates existing database to building-centric structure

**Usage:**
```bash
# Dry run (preview changes)
python3 reorganize_by_building.py true

# Execute reorganization
python3 reorganize_by_building.py false
```

**What it does:**
1. Groups apartments by address
2. Creates buildings collection
3. Adds building_id references to apartments
4. Calculates building-level stats
5. Creates database indexes

**Stats:**
- Creates ~75 buildings from 264 apartments
- Preserves all existing data
- Adds building_id references

---

### 2. Add Unit to Building Script

**File:** `/app/add_unit_to_building.py`

**Purpose:** Easy way to add new units to existing buildings

**Usage:**

**Interactive Mode:**
```bash
python3 add_unit_to_building.py
```

**List Buildings:**
```bash
# List all buildings
python3 add_unit_to_building.py list

# Search buildings
python3 add_unit_to_building.py list "Chelsea"
python3 add_unit_to_building.py list "Manhattan"
python3 add_unit_to_building.py list "Malt Drive"
```

**Interactive Workflow:**
1. Search for building (by name/address/neighborhood)
2. Select building from list
3. Enter unit details:
   - Unit number
   - Title
   - Bedrooms/bathrooms
   - Price
   - Square feet
   - Description
   - Images (optional)
4. Confirm and add

**Example:**
```
Search for building: Chelsea Place
Select building: 1

Enter unit details:
Unit Number: 3A
Bedrooms: 1
Bathrooms: 1
Price: 4500
Square feet: 700
...

✅ Unit added successfully!
```

---

## Benefits

### Before (Flat Structure)
```
apartments collection:
  - apartment1 (Chelsea Place 1BR)
  - apartment2 (Chelsea Place 2BR)
  - apartment3 (Malt Drive 2-20, Unit 414)
  - apartment4 (Malt Drive 2-20, Unit 320)
  ...
```

**Problems:**
- ❌ Hard to find all units in a building
- ❌ Duplicate building data in each apartment
- ❌ No easy way to add unit to existing building
- ❌ Building-level amenities repeated

### After (Hierarchical Structure)
```
buildings collection:
  - Chelsea Place® (id: xxx)
  - Malt Drive 2-20 (id: yyy)
  ...

apartments collection:
  - apartment1 (building_id: xxx, unit: E1YXVQTJ)
  - apartment2 (building_id: xxx, unit: MQEM1KAX)
  - apartment3 (building_id: yyy, unit: 414)
  - apartment4 (building_id: yyy, unit: 320)
  ...
```

**Advantages:**
- ✅ Easy to find all units in a building
- ✅ Building data stored once, referenced
- ✅ Simple script to add new units
- ✅ Better data integrity
- ✅ Easier to maintain

---

## Common Operations

### Finding All Units in a Building

**MongoDB:**
```javascript
// Find building
building = db.buildings.findOne({building_name: "Chelsea Place®"})

// Find all units
units = db.apartments.find({building_id: building.building_id})
```

**Python:**
```python
# Find building
building = buildings_collection.find_one({'building_name': 'Chelsea Place®'})

# Find all units
units = apartments_collection.find({'building_id': building['building_id']})
```

### Adding a New Unit

**Easy way:**
```bash
python3 add_unit_to_building.py
```

**Manual way:**
```python
from add_unit_to_building import add_unit_to_building

unit_data = {
    'unit_number': '3A',
    'title': '1BR at Chelsea Place®',
    'price': 4500,
    'bedrooms': 1,
    'bathrooms': 1,
    'sqft': 700,
    'images': ['https://...'],
    'description': '...'
}

add_unit_to_building('building_id_here', unit_data)
```

### Getting Building Stats

```python
# Get building with current stats
building = buildings_collection.find_one({'building_id': 'xxx'})

print(f"Total units: {building['total_units']}")
print(f"Available: {building['available_units']}")
print(f"Price range: ${building['price_range']['min']} - ${building['price_range']['max']}")
```

---

## Integration with Frontend

The frontend "View All Units" feature automatically uses building relationships:

```javascript
// Backend API
GET /api/apartments/{apartment_id}/similar-units

// Uses building_id to find all units in same building
const similarUnits = await db.apartments.find({
  building_id: apartment.building_id,
  id: {$ne: apartment.id}
})
```

---

## Data Migration Status

**Current Status:** Scripts created, ready to execute

**To Apply:**
```bash
# Preview changes
python3 reorganize_by_building.py true

# Apply changes (creates buildings collection)
python3 reorganize_by_building.py false
```

**Safe Migration:**
- ✅ Non-destructive (doesn't delete apartments)
- ✅ Adds building_id references
- ✅ Creates new buildings collection
- ✅ Preserves all existing data
- ✅ Can be reversed if needed

---

## Building Identification

The reorganization script intelligently identifies buildings:

**1. By Address (Primary)**
- Groups apartments with same address
- Example: "363 West 30th Street" → Chelsea Place building

**2. By Neighborhood (Fallback)**
- For apartments without addresses
- Example: "Greenpoint, Brooklyn" → Greenpoint building group

**3. Building Name**
- Uses building_name if provided
- Example: "Chelsea Place®", "Malt Drive 2-20"

---

## Examples

### Example 1: Manhattan Skyline Buildings

**Chelsea Place®**
- Address: 363 West 30th Street, New York, NY 10001
- Units: 2 (1BR for $4,400, 2BR for $7,050)
- Both units kept (different bedroom counts)

**Malt Drive 2-20**
- Address: 2-20 Malt Drive, LIC
- Units: 18 total (6 available)
- Studios and 2BRs

### Example 2: Adding New Manhattan Skyline Unit

**Scenario:** Chelsea Place just listed Unit 4B (1BR, $4,600)

```bash
python3 add_unit_to_building.py

Search: Chelsea Place
Select: 1. Chelsea Place® (363 West 30th Street)

Unit Number: 4B
Bedrooms: 1
Bathrooms: 1
Price: 4600
Square feet: 680
Description: Newly renovated 1BR with city views

✅ Added! Building now has 3 units.
```

---

## Maintenance

### Updating Building Stats

Building stats auto-update when units are added via script. Manual update:

```python
# Recalculate stats for a building
all_units = list(apartments_collection.find({'building_id': building_id}))
available = [u for u in all_units if u.get('available')]
prices = [u['price'] for u in all_units]

buildings_collection.update_one(
    {'building_id': building_id},
    {'$set': {
        'total_units': len(all_units),
        'available_units': len(available),
        'price_range': {
            'min': min(prices),
            'max': max(prices),
            'avg': sum(prices) / len(prices)
        }
    }}
)
```

### Finding Orphaned Apartments

```python
# Apartments without building_id
orphaned = apartments_collection.find({'building_id': {'$exists': False}})
```

---

## Next Steps

1. **Review dry-run output**
   ```bash
   python3 reorganize_by_building.py true
   ```

2. **Apply reorganization**
   ```bash
   python3 reorganize_by_building.py false
   ```

3. **Test adding a unit**
   ```bash
   python3 add_unit_to_building.py
   ```

4. **Update frontend to use buildings collection** (optional)
   - Show building details on unit pages
   - Better "View All Units" feature
   - Building-level search/filter

---

## Rollback Plan

If needed, rollback is simple:

```python
# Remove building_id references from apartments
apartments_collection.update_many(
    {},
    {'$unset': {'building_id': ''}}
)

# Drop buildings collection
db.buildings.drop()
```

All apartment data remains intact.
