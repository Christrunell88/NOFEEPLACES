# AI-Powered Listing Moderation System

## Overview
Automated listing quality control system using Emergent LLM (GPT-4o-mini) to analyze apartment listings for content quality, spam detection, duplicate detection, price accuracy, and automatic categorization.

## Features

### 1. Content Quality Analysis
- ✅ Description completeness and clarity
- ✅ Title professionalism
- ✅ Required field validation
- ✅ Grammar and readability assessment

### 2. Spam & Fraud Detection
- ✅ Scam pattern detection
- ✅ Suspicious contact information
- ✅ Unrealistic pricing (under $1000/month in NYC)
- ✅ Generic or misleading descriptions

### 3. Image Quality Assessment
- ✅ Relevance of images to listing
- ✅ Detection of stock photos
- ✅ Image count verification
- ✅ Professional photo quality scoring

### 4. Automatic Categorization
- ✅ Budget Friendly: $1,500 - $2,800/month
- ✅ Smart Value: $2,800 - $4,500/month
- ✅ Sky's the Limit: $4,500+/month
- ✅ Based on price, features, and amenities

### 5. Geographic Validation
- ✅ Neighborhood-Borough consistency check
- ✅ NYC geography database (all 5 boroughs)
- ✅ Common misspelling detection
- ✅ Suggestions for correct neighborhoods

### 6. Price Anomaly Detection
- ✅ Below-market pricing alerts (potential scams)
- ✅ Above-market pricing verification
- ✅ Borough-specific pricing expectations
- ✅ Bedroom count vs. price validation

### 7. Duplicate Detection
- ✅ AI-powered similarity analysis
- ✅ Address matching
- ✅ Generic title detection
- ✅ Image fingerprinting consideration

## How It Works

### Moderation Workflow

1. **Admin Selection** 
   - Admin selects listings from dashboard
   - Can moderate single listing or batch process
   - On-demand processing via Admin Dashboard

2. **AI Analysis**
   - Each listing sent to GPT-4o-mini with specialized prompt
   - Structured JSON response with scores (0-100)
   - Multiple validation checks run simultaneously

3. **Automated Decision**
   ```
   Auto-Approve: Content Score > 70 && Spam Prob < 30 && Image Score > 60
   Auto-Reject: Spam Prob > 70 || Critical Price Anomaly
   Manual Review: Borderline cases (all others)
   ```

4. **Database Update**
   - Moderation results saved to listing record
   - Auto-categorization applied
   - Timestamp and confidence scores stored

## API Endpoints

### POST /api/admin/moderate-listings
Moderate multiple listings in batch.

**Request:**
```json
{
  "listing_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response:**
```json
{
  "success": true,
  "total": 3,
  "approved": 2,
  "rejected": 0,
  "manual_review": 1,
  "failed": 0,
  "results": [...]
}
```

### POST /api/admin/moderate-single-listing?listing_id=uuid
Moderate a single listing with detailed analysis.

**Response:**
```json
{
  "success": true,
  "listing_id": "uuid",
  "moderation": {
    "content_quality_score": 85,
    "spam_probability": 15,
    "image_quality_score": 90,
    "recommended_category": "Smart Value",
    "final_decision": {
      "action": "approve",
      "reason": "High quality listing",
      "confidence": 92
    }
  }
}
```

### GET /api/admin/moderation-stats
Get overall moderation statistics.

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_listings": 259,
    "moderated": 150,
    "pending": 109,
    "approved": 120,
    "rejected": 10,
    "manual_review": 20,
    "moderation_rate": 57.92
  }
}
```

## Using the Admin Dashboard

### Step-by-Step Guide

1. **Login to Admin Dashboard**
   - Navigate to `/admin`
   - Login with admin credentials

2. **Access Moderation Tab**
   - Click "Moderation" in the navigation tabs
   - View moderation statistics at the top

3. **Select Listings**
   - Pending listings displayed in table
   - Click checkboxes to select individual listings
   - Or click "Select All" for batch processing

4. **Run Moderation**
   - Click "Moderate Selected Listings" button
   - AI analysis runs (typically 5-10 seconds per listing)
   - Progress indicator shows processing status

5. **Review Results**
   - Results displayed below with color-coded status:
     - 🟢 Green: Auto-Approved
     - 🔴 Red: Auto-Rejected
     - 🟡 Yellow: Needs Manual Review
   - Click on results to see detailed reasoning

6. **Take Action on Manual Reviews**
   - Navigate to "Apartments" tab
   - Filter by moderation status
   - Manually approve/reject flagged listings

## Moderation Criteria

### Auto-Approval Criteria
- Content quality score ≥ 70%
- Spam probability < 30%
- Image quality score ≥ 60%
- AI confidence ≥ 70%
- No critical price anomalies
- Valid neighborhood/borough

### Auto-Rejection Criteria
- Spam probability > 70%
- Price < $1,000/month (scam indicator)
- Multiple critical issues
- Clear fraud patterns
- AI confidence ≥ 80%

### Manual Review Triggers
- Borderline quality scores (40-70%)
- Medium spam probability (30-70%)
- Price anomalies with medium severity
- Missing critical information
- Conflicting signals
- AI confidence < 70%

## Technical Implementation

### Backend
- **File:** `/app/backend/listing_moderator.py`
- **LLM:** GPT-4o-mini via Emergent LLM Universal Key
- **Framework:** emergentintegrations library
- **Database:** MongoDB (moderation results stored in listing documents)

### Frontend
- **Component:** `ModerationPanel` in `/app/frontend/src/AdminDashboard.js`
- **Features:** Real-time stats, batch selection, progress indicators, result display

### Environment Variables
```
EMERGENT_LLM_KEY=sk-emergent-*** (already configured)
```

## Price Categories

### Budget Friendly ($1,500 - $2,800)
- Studios and 1-bedrooms
- Outer boroughs priority
- Good for first-time renters
- Essential amenities

### Smart Value ($2,800 - $4,500)
- 1-2 bedrooms
- Manhattan outer neighborhoods
- Brooklyn prime areas
- Modern amenities

### Sky's the Limit ($4,500+)
- 2+ bedrooms
- Manhattan prime locations
- Luxury amenities
- Doorman, concierge, gym

## Best Practices

### For Admins
1. **Regular Monitoring**: Check moderation stats weekly
2. **Batch Processing**: Moderate 10-20 listings at a time for efficiency
3. **Review AI Decisions**: Spot-check auto-approved listings
4. **Update Criteria**: Adjust thresholds based on results
5. **Manual Override**: Always available for edge cases

### For System Maintenance
1. **Monitor API Key Balance**: Check Emergent LLM key credits
2. **Review Logs**: Check backend logs for moderation errors
3. **Update NYC Data**: Keep neighborhood list current
4. **Adjust Prompts**: Refine AI prompts based on performance
5. **Performance Tracking**: Monitor approval/rejection rates

## Troubleshooting

### Issue: Moderation Takes Too Long
**Solution:** Reduce batch size to 5-10 listings at a time

### Issue: Too Many Manual Reviews
**Solution:** Adjust threshold scores in `_calculate_final_decision()` method

### Issue: API Key Credits Running Low
**Solution:** Add balance via Profile → Universal Key → Add Balance

### Issue: Inconsistent Categorization
**Solution:** Review and update price range definitions in `listing_moderator.py`

## Future Enhancements

- [ ] Multi-language support for international listings
- [ ] Advanced image analysis (computer vision integration)
- [ ] Historical pricing trends analysis
- [ ] Automated amenity extraction from descriptions
- [ ] Landlord reputation scoring
- [ ] Real-time moderation queue
- [ ] Email notifications for moderation decisions
- [ ] Batch scheduling (nightly auto-moderation)

## Support

For questions or issues:
- **Email:** placesfirm@gmail.com
- **Documentation:** This file
- **Backend Logs:** `/var/log/supervisor/backend.err.log`

---

**Last Updated:** January 2025
**Version:** 1.0
**Status:** Production Ready ✅
