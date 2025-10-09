#!/usr/bin/env python3
"""
Comprehensive Data Quality Audit for NoFeePlaces.com
Identifies all data quality issues across listings including:
- Unrealistic pricing for locations
- Fictional vs real apartments
- Image-price mismatches
- Address inconsistencies
- Missing or incorrect data
"""
import asyncio
import os
import requests
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

class DataQualityAuditor:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'nofeeplaces')
        
        # NYC Neighborhood Price Ranges (realistic market data)
        self.neighborhood_price_ranges = {
            'Manhattan': {
                'Tribeca': {'studio': (7000, 12000), '1br': (9000, 18000), '2br': (15000, 35000), '3br': (25000, 60000)},
                'SoHo': {'studio': (6500, 11000), '1br': (8500, 16000), '2br': (14000, 30000), '3br': (22000, 50000)},
                'Upper East Side': {'studio': (4500, 8000), '1br': (6000, 12000), '2br': (10000, 22000), '3br': (18000, 40000)},
                'Upper West Side': {'studio': (4200, 7500), '1br': (5500, 11000), '2br': (9500, 20000), '3br': (16000, 35000)},
                'Midtown East': {'studio': (5000, 9000), '1br': (7000, 14000), '2br': (12000, 25000), '3br': (20000, 45000)},
                'Midtown West': {'studio': (4800, 8500), '1br': (6500, 13000), '2br': (11000, 24000), '3br': (19000, 42000)},
                'Greenwich Village': {'studio': (5500, 9500), '1br': (7500, 15000), '2br': (13000, 28000), '3br': (22000, 48000)},
                'East Village': {'studio': (4000, 7000), '1br': (5500, 10000), '2br': (8500, 18000), '3br': (15000, 30000)},
                'Chelsea': {'studio': (5000, 8500), '1br': (7000, 13500), '2br': (11500, 25000), '3br': (20000, 43000)},
                'Financial District': {'studio': (4500, 7500), '1br': (6000, 11500), '2br': (9500, 20000), '3br': (16000, 35000)},
                'Hell\'s Kitchen': {'studio': (4200, 7200), '1br': (5800, 11000), '2br': (9000, 19000), '3br': (15500, 32000)},
                'Murray Hill': {'studio': (4000, 6800), '1br': (5200, 10000), '2br': (8000, 17000), '3br': (14000, 28000)},
                'Gramercy': {'studio': (4800, 8000), '1br': (6500, 12500), '2br': (10500, 22000), '3br': (18000, 38000)},
            },
            'Brooklyn': {
                'DUMBO': {'studio': (4000, 6500), '1br': (5500, 9500), '2br': (8000, 16000), '3br': (12000, 25000)},
                'Williamsburg': {'studio': (3500, 5800), '1br': (4800, 8500), '2br': (7000, 14000), '3br': (10500, 22000)},
                'Park Slope': {'studio': (3200, 5500), '1br': (4500, 8000), '2br': (6500, 13000), '3br': (9500, 20000)},
                'Brooklyn Heights': {'studio': (3800, 6000), '1br': (5200, 9000), '2br': (7500, 15000), '3br': (11000, 23000)},
                'Fort Greene': {'studio': (3000, 5000), '1br': (4200, 7200), '2br': (6000, 12000), '3br': (8500, 18000)},
                'Bed-Stuy': {'studio': (2500, 4200), '1br': (3500, 6000), '2br': (5000, 9500), '3br': (7000, 14000)},
                'Crown Heights': {'studio': (2200, 3800), '1br': (3000, 5200), '2br': (4200, 8000), '3br': (6000, 12000)},
            },
            'Queens': {
                'Long Island City': {'studio': (3200, 5200), '1br': (4200, 7000), '2br': (6000, 11000), '3br': (8500, 16000)},
                'Astoria': {'studio': (2800, 4500), '1br': (3800, 6200), '2br': (5200, 9500), '3br': (7500, 14000)},
                'Sunnyside': {'studio': (2500, 4000), '1br': (3300, 5500), '2br': (4500, 8200), '3br': (6500, 12000)},
            }
        }
        
        # Premium streets that command higher prices
        self.premium_streets = {
            'Central Park West': 1.4,  # 40% premium
            'Park Avenue': 1.35,      # 35% premium
            'Fifth Avenue': 1.5,      # 50% premium
            'Madison Avenue': 1.25,   # 25% premium
            'Broadway': 1.1,          # 10% premium (in premium areas)
            'Riverside Drive': 1.2,   # 20% premium
        }
        
    async def connect_database(self):
        """Connect to the database"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
    
    async def audit_all_listings(self):
        """Run comprehensive audit on all listings"""
        await self.connect_database()
        
        print("🔍 COMPREHENSIVE DATA QUALITY AUDIT")
        print("=" * 60)
        
        # Get all apartments
        apartments = await self.db.apartments.find({}).to_list(length=None)
        
        print(f"📊 Total Apartments: {len(apartments)}")
        print()
        
        issues = {
            'pricing_issues': [],
            'fictional_listings': [],
            'image_mismatches': [],
            'address_issues': [],
            'data_inconsistencies': []
        }
        
        for i, apt in enumerate(apartments, 1):
            print(f"Auditing {i}/{len(apartments)}: {apt.get('title', 'Unknown')[:50]}...")
            
            # Check pricing issues
            pricing_issue = self.check_pricing_realistic(apt)
            if pricing_issue:
                issues['pricing_issues'].append(pricing_issue)
            
            # Check for fictional listings
            fictional_issue = self.check_if_fictional(apt)
            if fictional_issue:
                issues['fictional_listings'].append(fictional_issue)
            
            # Check image-price mismatches
            image_issue = self.check_image_price_mismatch(apt)
            if image_issue:
                issues['image_mismatches'].append(image_issue)
            
            # Check address consistency
            address_issue = self.check_address_consistency(apt)
            if address_issue:
                issues['address_issues'].append(address_issue)
            
            # Check data consistency
            data_issue = self.check_data_consistency(apt)
            if data_issue:
                issues['data_inconsistencies'].append(data_issue)
        
        # Generate report
        self.generate_audit_report(issues)
        
        return issues
    
    def check_pricing_realistic(self, apt):
        """Check if pricing is realistic for the location"""
        price = apt.get('price', 0)
        neighborhood = apt.get('neighborhood', '')
        borough = apt.get('borough', '')
        bedrooms = apt.get('bedrooms', 0)
        address = apt.get('address', '')
        
        if not price or not neighborhood:
            return None
        
        # Determine bedroom type
        if bedrooms == 0 or bedrooms == 'Studio':
            bed_type = 'studio'
        elif bedrooms == 1:
            bed_type = '1br'
        elif bedrooms == 2:
            bed_type = '2br'
        elif bedrooms >= 3:
            bed_type = '3br'
        else:
            return None
        
        # Get expected price range
        if borough in self.neighborhood_price_ranges:
            if neighborhood in self.neighborhood_price_ranges[borough]:
                expected_range = self.neighborhood_price_ranges[borough][neighborhood].get(bed_type)
                
                if expected_range:
                    min_price, max_price = expected_range
                    
                    # Apply premium street multiplier
                    for street, multiplier in self.premium_streets.items():
                        if street in address:
                            min_price = int(min_price * multiplier)
                            max_price = int(max_price * multiplier)
                            break
                    
                    # Check if price is realistic (allow 20% variance below minimum)
                    if price < min_price * 0.8:
                        return {
                            'id': apt.get('id'),
                            'title': apt.get('title'),
                            'current_price': price,
                            'expected_range': (min_price, max_price),
                            'neighborhood': neighborhood,
                            'bedrooms': bedrooms,
                            'severity': 'high' if price < min_price * 0.5 else 'medium',
                            'issue': f'Price ${price} too low for {neighborhood} {bed_type}'
                        }
                    elif price > max_price * 1.5:
                        return {
                            'id': apt.get('id'),
                            'title': apt.get('title'),
                            'current_price': price,
                            'expected_range': (min_price, max_price),
                            'neighborhood': neighborhood,
                            'bedrooms': bedrooms,
                            'severity': 'medium',
                            'issue': f'Price ${price} unusually high for {neighborhood} {bed_type}'
                        }
        
        return None
    
    def check_if_fictional(self, apt):
        """Check if listing appears to be fictional"""
        title = apt.get('title', '')
        description = apt.get('description', '')
        address = apt.get('address', '')
        data_source = apt.get('data_source', '')
        
        # Red flags for fictional listings
        fictional_indicators = [
            'bulk_generator' in data_source.lower(),
            'generated' in data_source.lower(),
            not address or len(address) < 10,
            'Lorem ipsum' in description,
            title.startswith('Generated '),
            'Test apartment' in title.lower(),
            apt.get('created_at', '').startswith('2025-') and 'Verified' not in data_source
        ]
        
        fictional_score = sum(fictional_indicators)
        
        if fictional_score >= 2:
            return {
                'id': apt.get('id'),
                'title': title,
                'data_source': data_source,
                'fictional_score': fictional_score,
                'indicators': [i for i, flag in enumerate(fictional_indicators) if flag],
                'severity': 'high' if fictional_score >= 3 else 'medium'
            }
        
        return None
    
    def check_image_price_mismatch(self, apt):
        """Check if images don't match the price point"""
        price = apt.get('price', 0)
        images = apt.get('images', [])
        
        if not images or not price:
            return None
        
        # Basic heuristic: luxury stock photos with budget prices
        luxury_image_indicators = [
            'pexels' in img.lower() and any(term in img.lower() 
                for term in ['luxury', 'modern', 'apartment', 'interior']) 
            for img in images[:3]  # Check first 3 images
        ]
        
        has_luxury_images = sum(luxury_image_indicators) >= 2
        
        # If price is very low but images suggest luxury
        if has_luxury_images and price < 3000:
            return {
                'id': apt.get('id'),
                'title': apt.get('title'),
                'price': price,
                'image_count': len(images),
                'first_image': images[0] if images else '',
                'severity': 'high',
                'issue': 'Luxury stock images with budget price'
            }
        
        return None
    
    def check_address_consistency(self, apt):
        """Check address and location consistency"""
        address = apt.get('address', '')
        neighborhood = apt.get('neighborhood', '')
        borough = apt.get('borough', '')
        location = apt.get('location', '')
        
        issues = []
        
        # Check borough consistency
        if 'Manhattan' in address and borough != 'Manhattan':
            issues.append('Borough mismatch in address')
        elif 'Brooklyn' in address and borough != 'Brooklyn':
            issues.append('Borough mismatch in address')
        elif 'Queens' in address and borough != 'Queens':
            issues.append('Borough mismatch in address')
        
        # Check ZIP code consistency (basic check)
        manhattan_zips = ['10001', '10002', '10003', '10009', '10010', '10011', '10012', '10013', '10014', '10016', '10017', '10018', '10019', '10020', '10021', '10022', '10023', '10024', '10025', '10026', '10027', '10028', '10029', '10030', '10031', '10032', '10033', '10034', '10035', '10036', '10037', '10038', '10039', '10040']
        
        if borough == 'Manhattan':
            zip_in_address = None
            for zip_code in manhattan_zips:
                if zip_code in address:
                    zip_in_address = zip_code
                    break
            
            if not zip_in_address:
                issues.append('Manhattan apartment missing valid Manhattan ZIP code')
        
        if issues:
            return {
                'id': apt.get('id'),
                'title': apt.get('title'),
                'address': address,
                'neighborhood': neighborhood,
                'borough': borough,
                'issues': issues,
                'severity': 'medium'
            }
        
        return None
    
    def check_data_consistency(self, apt):
        """Check internal data consistency"""
        issues = []
        
        # Check required fields
        required_fields = ['title', 'price', 'bedrooms', 'bathrooms', 'neighborhood', 'borough']
        for field in required_fields:
            if not apt.get(field):
                issues.append(f'Missing {field}')
        
        # Check data types
        if apt.get('price') and not isinstance(apt.get('price'), (int, float)):
            issues.append('Price not numeric')
        
        if apt.get('bedrooms') not in [0, 1, 2, 3, 4, 5, 'Studio']:
            issues.append('Invalid bedrooms value')
        
        # Check images
        images = apt.get('images', [])
        if len(images) < 1:
            issues.append('No images')
        elif len(images) > 10:
            issues.append('Too many images')
        
        if issues:
            return {
                'id': apt.get('id'),
                'title': apt.get('title'),
                'issues': issues,
                'severity': 'low' if len(issues) <= 2 else 'medium'
            }
        
        return None
    
    def generate_audit_report(self, issues):
        """Generate comprehensive audit report"""
        print("\n" + "=" * 80)
        print("📋 DATA QUALITY AUDIT REPORT")
        print("=" * 80)
        
        # Summary
        total_issues = sum(len(issue_list) for issue_list in issues.values())
        print(f"🚨 TOTAL ISSUES FOUND: {total_issues}")
        print()
        
        # Pricing Issues
        pricing_issues = issues['pricing_issues']
        print(f"💰 PRICING ISSUES: {len(pricing_issues)}")
        if pricing_issues:
            high_severity = [i for i in pricing_issues if i['severity'] == 'high']
            print(f"   High Severity: {len(high_severity)}")
            for issue in high_severity[:5]:  # Show first 5
                print(f"   • {issue['title'][:40]}... - ${issue['current_price']} (expected ${issue['expected_range'][0]}-${issue['expected_range'][1]})")
            if len(high_severity) > 5:
                print(f"   ... and {len(high_severity) - 5} more high severity pricing issues")
        print()
        
        # Fictional Listings
        fictional = issues['fictional_listings']
        print(f"🤖 FICTIONAL LISTINGS: {len(fictional)}")
        if fictional:
            for issue in fictional[:3]:
                print(f"   • {issue['title'][:50]}... (Score: {issue['fictional_score']}/7)")
        print()
        
        # Image Mismatches
        image_issues = issues['image_mismatches']
        print(f"🖼️ IMAGE-PRICE MISMATCHES: {len(image_issues)}")
        if image_issues:
            for issue in image_issues[:3]:
                print(f"   • {issue['title'][:40]}... - ${issue['price']} with luxury images")
        print()
        
        # Address Issues
        address_issues = issues['address_issues']
        print(f"📍 ADDRESS INCONSISTENCIES: {len(address_issues)}")
        if address_issues:
            for issue in address_issues[:3]:
                print(f"   • {issue['title'][:40]}... - {', '.join(issue['issues'])}")
        print()
        
        # Data Issues
        data_issues = issues['data_inconsistencies']
        print(f"📊 DATA INCONSISTENCIES: {len(data_issues)}")
        if data_issues:
            for issue in data_issues[:3]:
                print(f"   • {issue['title'][:40]}... - {', '.join(issue['issues'])}")
        print()
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"/app/data_quality_report_{timestamp}.json"
        
        import json
        with open(report_file, 'w') as f:
            json.dump(issues, f, indent=2, default=str)
        
        print(f"💾 Detailed report saved to: {report_file}")
        print()
        print("🎯 RECOMMENDED ACTIONS:")
        print("1. Fix high-severity pricing issues immediately")
        print("2. Remove or replace fictional listings with real data")
        print("3. Update images to match price points")
        print("4. Correct address inconsistencies")
        print("5. Fill in missing required data fields")
    
    async def close_connection(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close()

async def main():
    auditor = DataQualityAuditor()
    try:
        issues = await auditor.audit_all_listings()
        return issues
    finally:
        await auditor.close_connection()

if __name__ == "__main__":
    asyncio.run(main())