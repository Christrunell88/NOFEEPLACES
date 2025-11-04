# Deploy Fix to Production

## The Issue
You're still seeing the $2,344 Central Park West apartment because the fix is only in **local development**. The **production environment** needs to be updated.

## What Needs to be Deployed
The updated `/app/backend/server.py` file that contains:
- New admin endpoint: `POST /api/admin/fix-central-park-west`
- Fix that updates apartment from $2,344 → $7,500

## Deployment Steps

### Step 1: Deploy Backend Code
Deploy the updated `/app/backend/server.py` to your production environment:

```bash
# If using git deployment:
git add backend/server.py
git commit -m "Add admin endpoint to fix Central Park West pricing"
git push production

# Or copy the file to production server:
scp /app/backend/server.py production-server:/path/to/backend/
```

### Step 2: Restart Production Backend
```bash
# On production server:
sudo systemctl restart backend
# Or whatever command restarts your production backend
```

### Step 3: Apply the Fix
Once deployed, call the admin endpoint:
```bash
curl -X POST "https://buildingtracker-1.preview.emergentagent.com/api/admin/fix-central-park-west"
```

### Step 4: Verify
- Refresh your browser
- Check if apartment now shows $7,500 instead of $2,344

## Alternative: Manual Database Fix
If deployment takes time, you can fix the database directly:

```javascript
// Connect to production MongoDB and run:
db.apartments.updateOne(
  {id: 'c00cb712-9466-4f1a-9a6b-353bf7e5978e'},
  {$set: {
    price: 7500,
    title: 'Luxury Studio on Central Park West - No Fee',
    updated_at: new Date(),
    quality_score: 95
  }}
)
```

## Expected Result
```
Before: Modern Studio on Central Park West - No Fee - $2,344/mo
After:  Luxury Studio on Central Park West - No Fee - $7,500/mo
```