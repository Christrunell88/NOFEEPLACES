#!/usr/bin/env python3
"""
Real-time Data Quality Monitor for NoFeePlaces.com
Prevents bad data from entering the system and monitors ongoing quality
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

class DataQualityMonitor:
    def __init__(self):
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'nofeeplaces')
        
        # Validation rules
        self.price_ranges = {
            'Manhattan': {
                'studio': (4000, 12000),
                '1br': (5500, 18000),
                '2br': (9000, 35000),
                '3br': (15000, 60000)
            },
            'Brooklyn': {
                'studio': (2200, 6500),
                '1br': (3000, 9500),
                '2br': (4200, 16000),
                '3br': (6000, 25000)
            },
            'Queens': {
                'studio': (2500, 5200),
                '1br': (3300, 7000),
                '2br': (4500, 11000),
                '3br': (6500, 16000)
            }
        }
    
    async def connect_database(self):
        """Connect to database"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
    
    async def validate_apartment(self, apartment_data):
        """Validate apartment data before insertion"""
        errors = []
        warnings = []
        
        # Required fields check
        required_fields = ['title', 'price', 'bedrooms', 'bathrooms', 'neighborhood', 'borough']
        for field in required_fields:
            if not apartment_data.get(field):
                errors.append(f'Missing required field: {field}')
        
        # Price validation
        price = apartment_data.get('price', 0)
        bedrooms = apartment_data.get('bedrooms', 0)
        borough = apartment_data.get('borough', '')
        
        if price and bedrooms is not None and borough:
            bed_type = 'studio' if bedrooms == 0 else f'{bedrooms}br'
            if bed_type in ['studio', '1br', '2br', '3br'] and borough in self.price_ranges:
                expected_range = self.price_ranges[borough].get(bed_type)
                if expected_range:
                    min_price, max_price = expected_range
                    if price < min_price * 0.7:  # 30% below minimum
                        errors.append(f'Price ${price} too low for {borough} {bed_type} (expected ${min_price}-${max_price})')
                    elif price > max_price * 1.3:  # 30% above maximum
                        warnings.append(f'Price ${price} unusually high for {borough} {bed_type} (expected ${min_price}-${max_price})')
        
        # Image validation
        images = apartment_data.get('images', [])
        if len(images) < 1:
            errors.append('At least one image required')
        elif len(images) > 10:
            warnings.append('Too many images (>10)')
        
        # Contact validation
        contact_email = apartment_data.get('contact_email', '')
        if contact_email and 'placesfirm@gmail.com' not in contact_email:
            warnings.append('Non-standard contact email detected')
        
        # Data source validation
        data_source = apartment_data.get('data_source', '')
        if any(term in data_source.lower() for term in ['generated', 'bulk', 'test', 'fake']):
            errors.append(f'Suspicious data source: {data_source}')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'quality_score': max(0, 100 - len(errors) * 20 - len(warnings) * 5)
        }
    
    async def monitor_recent_additions(self, hours=24):
        """Monitor recently added apartments for quality issues"""
        await self.connect_database()
        
        print(f"🔍 MONITORING APARTMENTS ADDED IN LAST {hours} HOURS")
        print("=" * 60)
        
        # Get recent apartments
        from datetime import timedelta
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        recent_apartments = await self.db.apartments.find({
            'created_at': {'$gte': cutoff_time.isoformat()}
        }).to_list(length=None)
        
        print(f"Found {len(recent_apartments)} recent apartments")
        
        issues_found = 0
        
        for apt in recent_apartments:
            validation_result = await self.validate_apartment(apt)
            
            if not validation_result['valid'] or validation_result['warnings']:
                issues_found += 1
                print(f"\n⚠️  ISSUE: {apt.get('title', 'Unknown')[:50]}...")
                
                if validation_result['errors']:
                    print(f"   Errors: {validation_result['errors']}")
                
                if validation_result['warnings']:
                    print(f"   Warnings: {validation_result['warnings']}")
                
                print(f"   Quality Score: {validation_result['quality_score']}/100")
        
        if issues_found == 0:
            print("\n✅ All recent apartments pass quality checks!")
        else:
            print(f"\n🚨 Found {issues_found} apartments with quality issues")
        
        return issues_found
    
    async def generate_quality_report(self):
        """Generate overall quality report"""
        await self.connect_database()
        
        print("\n📊 OVERALL DATA QUALITY REPORT")
        print("=" * 50)
        
        # Get all apartments
        all_apartments = await self.db.apartments.find({}).to_list(length=None)
        
        total_count = len(all_apartments)
        verified_count = sum(1 for apt in all_apartments if apt.get('is_verified'))
        high_quality_count = sum(1 for apt in all_apartments if apt.get('quality_score', 0) >= 90)
        
        # Borough distribution
        borough_counts = {}
        price_distribution = {'under_3k': 0, '3k_to_6k': 0, '6k_to_10k': 0, 'over_10k': 0}
        
        for apt in all_apartments:
            borough = apt.get('borough', 'Unknown')
            borough_counts[borough] = borough_counts.get(borough, 0) + 1
            
            price = apt.get('price', 0)
            if price < 3000:
                price_distribution['under_3k'] += 1
            elif price < 6000:
                price_distribution['3k_to_6k'] += 1
            elif price < 10000:
                price_distribution['6k_to_10k'] += 1
            else:
                price_distribution['over_10k'] += 1
        
        print(f"Total Apartments: {total_count}")
        print(f"Verified Listings: {verified_count} ({verified_count/total_count*100:.1f}%)")
        print(f"High Quality (90+): {high_quality_count} ({high_quality_count/total_count*100:.1f}%)")
        
        print("\nBorough Distribution:")
        for borough, count in borough_counts.items():
            print(f"   {borough}: {count} ({count/total_count*100:.1f}%)")
        
        print("\nPrice Distribution:")
        for range_name, count in price_distribution.items():
            print(f"   {range_name}: {count} ({count/total_count*100:.1f}%)")
        
        # Quality metrics
        quality_issues = 0
        for apt in all_apartments:
            validation = await self.validate_apartment(apt)
            if not validation['valid']:
                quality_issues += 1
        
        quality_percentage = (total_count - quality_issues) / total_count * 100 if total_count > 0 else 0
        
        print(f"\nOverall Quality Score: {quality_percentage:.1f}%")
        print(f"Apartments with Issues: {quality_issues}/{total_count}")
        
        return {
            'total_apartments': total_count,
            'verified_count': verified_count,
            'high_quality_count': high_quality_count,
            'quality_percentage': quality_percentage,
            'borough_distribution': borough_counts,
            'price_distribution': price_distribution
        }
    
    async def close_connection(self):
        """Close database connection"""
        if hasattr(self, 'client'):
            self.client.close()

async def main():
    """Main monitoring function"""
    monitor = DataQualityMonitor()
    
    try:
        # Monitor recent additions
        recent_issues = await monitor.monitor_recent_additions(24)
        
        # Generate quality report
        quality_report = await monitor.generate_quality_report()
        
        print("\n" + "=" * 70)
        print("📈 MONITORING COMPLETE")
        print("=" * 70)
        
        if recent_issues == 0 and quality_report['quality_percentage'] > 95:
            print("✅ EXCELLENT: Data quality is high across all metrics")
        elif quality_report['quality_percentage'] > 85:
            print("🟡 GOOD: Data quality is acceptable but watch for issues")
        else:
            print("🔴 ATTENTION NEEDED: Significant data quality issues detected")
        
        return quality_report
        
    finally:
        await monitor.close_connection()

if __name__ == "__main__":
    asyncio.run(main())