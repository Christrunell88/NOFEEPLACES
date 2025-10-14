# Central Park West Fix - Deployment Checklist

## Issue
- **Problem**: "Modern Studio on Central Park West - No Fee" showing $2,344 (unrealistic)
- **Impact**: Users see unrealistic pricing in preview
- **ID**: `c00cb712-9466-4f1a-9a6b-353bf7e5978e`

## Solution Ready
- [x] Admin endpoint added to `/app/backend/server.py`
- [x] Endpoint: `POST /api/admin/fix-central-park-west`
- [x] Will update price from $2,344 → $7,500
- [x] Will add luxury images and verification

## Deployment Steps

### Option 1: Quick Fix (Recommended)
- [ ] Deploy updated `/app/backend/server.py` to production
- [ ] Restart production backend service
- [ ] Call admin endpoint: `curl -X POST 'https://production-api/api/admin/fix-central-park-west'`
- [ ] Verify fix in preview

### Option 2: Direct Database
- [ ] Access production MongoDB
- [ ] Run update command:
  ```javascript
  db.apartments.updateOne(
    {id: 'c00cb712-9466-4f1a-9a6b-353bf7e5978e'},
    {$set: {
      price: 7500,
      title: 'Luxury Studio on Central Park West - No Fee',
      quality_score: 95
    }}
  )
  ```
- [ ] Verify fix in preview

### Option 3: Full Database Sync
- [ ] Use deployment package: `/app/production_deployment_20251009_164508/`
- [ ] Follow deployment instructions
- [ ] This fixes ALL apartments, not just Central Park West

## Verification
- [ ] Refresh browser preview
- [ ] Search "Central Park West"
- [ ] Confirm price is $7,500 (not $2,344)
- [ ] Check images match luxury tier
- [ ] Verify contact info is placesfirm@gmail.com

## Expected Result
```
Before: Modern Studio on Central Park West - No Fee - $2,344/mo
After:  Luxury Studio on Central Park West - No Fee - $7,500/mo
```

## Notes
- Fix only affects the one problematic apartment
- Does not remove apartment from inventory
- Updates to realistic NYC Central Park West pricing
- Maintains competitive apartment count (149+ units)
