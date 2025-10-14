#!/usr/bin/env python3

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import uuid
import os

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces_db')
client = AsyncIOMotorClient(mongo_url)
db = client.nofeeplaces_database

async def add_waterline_square_apartments():
    """Add 8 diverse Waterline Square apartments to the database"""
    
    waterline_apartments = [
        {
            "id": str(uuid.uuid4()),
            "title": "Luxury Studio at Waterline Square - Hudson River Views",
            "address": "400 West 61st Street, Unit 1818, New York, NY 10023",
            "neighborhood": "Upper West Side",
            "borough": "Manhattan",
            "price": 6229,
            "bedrooms": "Studio",
            "bathrooms": 1,
            "square_feet": 575,
            "description": "Experience luxury living in this stunning studio at Waterline Square with exceptional Hudson River views. This 575 sq ft residence features floor-to-ceiling windows, custom roller shades, and thoughtful layouts that maximize space. The gourmet kitchen includes Caesarstone countertops, wood paneled cabinetry, and stainless steel Bosch appliances. Enjoy access to 100,000 sq ft of amenities including fitness facilities, indoor pool, tennis courts, and The Waterline Club.",
            "amenities": [
                "100,000 sq ft of luxury amenities",
                "25-meter lap pool and spa facilities",
                "Tennis, basketball, and squash courts", 
                "30-ft rock climbing wall",
                "Golf simulator and indoor skate park",
                "24/7 Ritz-Carlton trained concierge",
                "Rooftop terraces with Hudson River views",
                "Pet spa and dog training facilities",
                "Business center and co-working spaces",
                "Wine storage and tasting room"
            ],
            "images": [
                "https://spcdn.shortpixel.ai/spio/ret_img,q_orig,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2025/08/floorplan-waterline-2-s4-542931.jpg",
                "https://spcdn.shortpixel.ai/spio/ret_img,q_orig,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/Interior_Kitchen_WaterlineSquare_Rental-wsq2-featured-4-1440x720-1.jpg"
            ],
            "available_date": datetime.utcnow(),
            "lease_terms": ["12 months", "24 months"],
            "pet_policy": "Pet Friendly - Cats and Dogs Welcome",
            "parking": "Available separately through MTP Parking (212) 575-5335",
            "utilities": "Electricity usage-based, Heat/Hot Water included",
            "contact_info": {
                "name": "Chris Trunell",
                "phone": "(646) 408-8048", 
                "email": "placesnyc88@gmail.com"
            },
            "features": [
                "Floor-to-ceiling windows",
                "Hudson River views",
                "In-unit washer/dryer",
                "Custom roller shades",
                "Keyless entry",
                "Central HVAC system",
                "Gourmet kitchen",
                "Caesarstone countertops",
                "Stainless steel appliances"
            ],
            "transportation": [
                "Columbus Circle - A, B, C, D trains (5 min walk)",
                "59th St-Columbus Circle - N, Q, R, W trains (5 min walk)", 
                "Multiple bus lines on Broadway and West End Avenue",
                "Easy access to Lincoln Tunnel and FDR Drive"
            ],
            "is_no_fee": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "property_management": "Windsor Communities",
            "building_year": 2019,
            "floor_plan": "Studio S4"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Spacious 1BR at Waterline Square - Modern Luxury Living",
            "address": "400 West 61st Street, Unit 308, New York, NY 10023", 
            "neighborhood": "Upper West Side",
            "borough": "Manhattan",
            "price": 7496,
            "bedrooms": 1,
            "bathrooms": 1,
            "square_feet": 835,
            "description": "This elegant 1-bedroom apartment at Waterline Square offers 835 sq ft of sophisticated living space with exceptional finishes and stunning city views. The residence features an open kitchen with waterfall island, walk-in closets, and floor-to-ceiling windows. Residents enjoy exclusive access to The Waterline Club's unprecedented amenity program including fitness facilities, pools, courts, and social spaces.",
            "amenities": [
                "100,000 sq ft of luxury amenities",
                "Indoor tennis and basketball courts",
                "Fitness center with boxing and yoga studios",
                "25-meter lap pool with hot tub",
                "Steam rooms and massage facilities",
                "Golf simulator and bowling alley",
                "Children's playroom designed by Roto",
                "Art and music studios",
                "24/7 concierge and doorman service",
                "Private dining rooms"
            ],
            "images": [
                "https://spcdn.shortpixel.ai/spio/ret_img,q_orig,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2025/08/floorplan-waterline-2-a21-542885.jpg",
                "https://spcdn.shortpixel.ai/spio/ret_img,q_orig,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/Interior_Kitchen_WaterlineSquare_Rental-wsq2-featured-4-1440x720-1.jpg"
            ],
            "available_date": datetime.utcnow(),
            "lease_terms": ["12 months", "24 months"],
            "pet_policy": "Pet Friendly - Cats and Dogs Welcome with pet amenities",
            "parking": "Available separately through MTP Parking",
            "utilities": "Electricity usage-based, Heat/Hot Water included",
            "contact_info": {
                "name": "Chris Trunell", 
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com"
            },
            "features": [
                "Open kitchen with waterfall island",
                "Floor-to-ceiling windows",
                "Walk-in closets",
                "Wood floors throughout",
                "In-unit Bosch washer/dryer",
                "Central air conditioning", 
                "Custom cabinetry",
                "Stainless steel appliances",
                "Marble bathroom finishes"
            ],
            "transportation": [
                "Lincoln Center - 1, 2, 3 trains (3 min walk)",
                "59th St-Columbus Circle - Multiple subway lines (5 min walk)",
                "Central Park West bus lines", 
                "Direct access to West Side Highway"
            ],
            "is_no_fee": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "property_management": "Windsor Communities",
            "building_year": 2019,
            "floor_plan": "1BR A21"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Premium 1BR with Den - Waterline Square Upper West Side",
            "address": "400 West 61st Street, Unit 310, New York, NY 10023",
            "neighborhood": "Upper West Side", 
            "borough": "Manhattan",
            "price": 9995,
            "bedrooms": 1,
            "bathrooms": 1.5,
            "square_feet": 1106,
            "description": "Discover elevated living in this premium 1-bedroom plus den apartment featuring 1,106 sq ft of meticulously designed space. This exceptional residence includes a separate home office, powder room, and expansive living areas with stunning Manhattan views. The gourmet kitchen features integrated appliances, and the spa-inspired bathroom boasts marble finishes. Experience unparalleled luxury with access to The Waterline Club's world-class amenities.",
            "amenities": [
                "The Waterline Club - 100,000 sq ft lifestyle destination",
                "Professional fitness facilities and personal training",
                "Multiple sports courts and fields",
                "Aquatic center with lap pool and spa",
                "Social lounges and entertainment spaces",
                "Business center and conference rooms",
                "Concierge and valet services",
                "Package receiving and storage",
                "Pet care facilities and training",
                "Rooftop gardens and terraces"
            ],
            "images": [
                "https://spcdn.shortpixel.ai/spio/ret_img,q_orig,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2025/08/floorplan-waterline-2-a22-542886.jpg",
                "https://spcdn.shortpixel.ai/spio/ret_img,q_orig,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/Interior_Kitchen_WaterlineSquare_Rental-wsq2-featured-4-1440x720-1.jpg"
            ],
            "available_date": datetime.utcnow(),
            "lease_terms": ["12 months", "18 months", "24 months"],
            "pet_policy": "Pet Friendly with dedicated pet amenities",
            "parking": "Valet parking available through building",
            "utilities": "Heat, Hot Water included. Electricity usage-based",
            "contact_info": {
                "name": "Chris Trunell",
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com"  
            },
            "features": [
                "Separate home office/den",
                "Powder room (1.5 baths)",
                "Floor-to-ceiling windows", 
                "Manhattan skyline views",
                "Gourmet kitchen with island",
                "Integrated appliances",
                "Custom storage solutions",
                "Marble bathroom finishes",
                "In-unit laundry"
            ],
            "transportation": [
                "Multiple subway lines at Columbus Circle (4 min walk)",
                "Lincoln Center area transportation hub",
                "Broadway and Amsterdam Avenue bus routes",
                "Convenient to all major NYC highways"
            ],
            "is_no_fee": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "property_management": "Windsor Communities", 
            "building_year": 2019,
            "floor_plan": "1BR A22 with Den"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Sophisticated 2BR/2BA at Waterline Square - River Views",
            "address": "400 West 61st Street, Unit 421, New York, NY 10023",
            "neighborhood": "Upper West Side",
            "borough": "Manhattan", 
            "price": 13357,
            "bedrooms": 2,
            "bathrooms": 2,
            "square_feet": 1474,
            "description": "Experience refined luxury in this spacious 2-bedroom, 2-bathroom residence spanning 1,474 sq ft with breathtaking Hudson River views. This thoughtfully designed home features two full bathrooms, expansive living areas, and a gourmet kitchen with premium finishes. The master suite includes a walk-in closet and spa-like ensuite bathroom. Enjoy world-class amenities and prime Upper West Side location steps from Central Park and Lincoln Center.",
            "amenities": [
                "Exclusive access to The Waterline Club",
                "Indoor and outdoor sports facilities", 
                "State-of-the-art fitness center",
                "Swimming pool and aquatic facilities",
                "Tennis and basketball courts",
                "Rock climbing wall and golf simulator",
                "Multiple lounges and social spaces",
                "Screening room and performance space",
                "24/7 concierge and security",
                "Landscaped terraces and gardens"
            ],
            "images": [
                "https://spcdn.shortpixel.ai/spio/ret_img,q_orig,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2025/08/floorplan-waterline-2-b2-542909.jpg",
                "https://spcdn.shortpixel.ai/spio/ret_img,q_orig,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/Interior_Kitchen_WaterlineSquare_Rental-wsq2-featured-4-1440x720-1.jpg"
            ],
            "available_date": datetime.utcnow(),
            "lease_terms": ["12 months", "24 months"],
            "pet_policy": "Pet Friendly - Full pet amenities and services",
            "parking": "Valet and self-parking options available",
            "utilities": "Heat, Hot Water, and Gas included. Electricity separate",
            "contact_info": {
                "name": "Chris Trunell",
                "phone": "(646) 408-8048", 
                "email": "placesnyc88@gmail.com"
            },
            "features": [
                "Hudson River views",
                "Master suite with walk-in closet",
                "Two full bathrooms",
                "Gourmet kitchen with island",
                "Floor-to-ceiling windows throughout", 
                "Premium appliance package",
                "Custom built-ins",
                "Marble and stone finishes",
                "Central air and heating"
            ],
            "transportation": [
                "59th St-Columbus Circle subway hub (3 min walk)", 
                "Lincoln Center transportation (2 min walk)",
                "Multiple bus lines on Columbus Avenue",
                "Easy access to Central Park and Riverside Drive"
            ],
            "is_no_fee": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "property_management": "Windsor Communities",
            "building_year": 2019,
            "floor_plan": "2BR B2"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Luxurious 2BR/2.5BA Duplex Style - Waterline Square Premium",
            "address": "400 West 61st Street, Unit 724, New York, NY 10023",
            "neighborhood": "Upper West Side",
            "borough": "Manhattan",
            "price": 14377,
            "bedrooms": 2,
            "bathrooms": 2.5,
            "square_feet": 1324, 
            "description": "This exceptional 2-bedroom, 2.5-bathroom residence offers 1,324 sq ft of sophisticated living space with premium finishes and stunning city views. The apartment features a powder room for guests, spacious bedrooms with ensuite bathrooms, and an open-concept living area perfect for entertaining. The gourmet kitchen includes top-of-the-line appliances and custom cabinetry. Residents enjoy unparalleled access to Waterline Square's extensive amenity program.",
            "amenities": [
                "The Waterline Club luxury amenity program",
                "Professional-grade fitness facilities",
                "Swimming and spa complex", 
                "Indoor sports courts and simulator",
                "Creative studios for art and music",
                "Multiple dining and entertainment spaces",
                "Children's facilities and programming",
                "Pet services and amenities",
                "Concierge and lifestyle services", 
                "Private event spaces"
            ],
            "images": [
                "https://spcdn.shortpixel.ai/spio/ret_img,q_orig,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2025/08/floorplan-waterline-2-b4-542915.jpg",
                "https://spcdn.shortpixel.ai/spio/ret_img,q_orig,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/Interior_Kitchen_WaterlineSquare_Rental-wsq2-featured-4-1440x720-1.jpg"
            ],
            "available_date": datetime.utcnow(),
            "lease_terms": ["12 months", "18 months", "24 months"],
            "pet_policy": "Pet Friendly with full amenity access",
            "parking": "Garage parking available with valet service", 
            "utilities": "Heat, Hot Water included. Electric and Cable separate",
            "contact_info": {
                "name": "Chris Trunell",
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com"
            },
            "features": [
                "2.5 bathrooms including powder room",
                "Open-concept living and dining",
                "Gourmet kitchen with premium finishes",
                "Master bedroom with ensuite bathroom", 
                "Guest bedroom with full bathroom",
                "Floor-to-ceiling windows",
                "Custom storage throughout",
                "High-end appliance package",
                "Designer lighting and fixtures"
            ],
            "transportation": [
                "Columbus Circle transportation hub (4 min walk)",
                "Lincoln Center subway access (3 min walk)",
                "West Side Highway access",
                "Multiple bus routes on major avenues"
            ],
            "is_no_fee": True, 
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "property_management": "Windsor Communities",
            "building_year": 2019,
            "floor_plan": "2BR B4"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Spectacular 3BR/2.5BA - Waterline Square Luxury Residence",
            "address": "400 West 61st Street, Unit 2303, New York, NY 10023",
            "neighborhood": "Upper West Side",
            "borough": "Manhattan",
            "price": 19060, 
            "bedrooms": 3,
            "bathrooms": 2.5,
            "square_feet": 1557,
            "description": "This magnificent 3-bedroom, 2.5-bathroom residence offers 1,557 sq ft of exceptional living space with panoramic city and river views. The home features three generously sized bedrooms, including a master suite with walk-in closet, plus a powder room for guests. The open-plan living area and gourmet kitchen create perfect spaces for both daily living and entertaining. Experience the pinnacle of luxury living with access to The Waterline Club's unmatched amenities.",
            "amenities": [
                "100,000+ sq ft of world-class amenities",
                "Multiple fitness studios and personal training", 
                "Aquatic center with pools and spa services",
                "Tennis, basketball, squash courts",
                "Golf simulator and rock climbing wall",
                "Social clubs and entertainment venues",
                "Business facilities and meeting rooms",
                "Concierge and valet services",
                "Pet care and training facilities",
                "Rooftop spaces and gardens"
            ],
            "images": [
                "https://spcdn.shortpixel.ai/spio/ret_img,q_orig,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2025/08/floorplan-waterline-1-c1-542870.jpg",
                "https://spcdn.shortpixel.ai/spio/ret_img,q_orig,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/Interior_Kitchen_WaterlineSquare_Rental-wsq2-featured-4-1440x720-1.jpg"
            ],
            "available_date": datetime.utcnow(),
            "lease_terms": ["12 months", "24 months"],
            "pet_policy": "Pet Friendly - Premium pet amenities and services",
            "parking": "Valet parking and storage available",
            "utilities": "Heat, Hot Water, Gas included. Electricity usage-based", 
            "contact_info": {
                "name": "Chris Trunell",
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com"
            },
            "features": [
                "Panoramic city and river views",
                "Master suite with walk-in closet",
                "Three spacious bedrooms",
                "2.5 bathrooms including powder room",
                "Open-plan living and dining areas", 
                "Gourmet kitchen with island",
                "Floor-to-ceiling windows",
                "Premium finishes throughout",
                "In-unit laundry room"
            ],
            "transportation": [
                "Columbus Circle - Multiple subway lines (5 min walk)",
                "Lincoln Center area transportation (4 min walk)", 
                "Bus routes on Broadway and Amsterdam",
                "Central Park West and Riverside Drive access"
            ],
            "is_no_fee": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "property_management": "Windsor Communities",
            "building_year": 2019,
            "floor_plan": "3BR C1"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Penthouse-Style 3BR/3.5BA - Waterline Square Trophy Unit", 
            "address": "400 West 61st Street, Unit 1408, New York, NY 10023",
            "neighborhood": "Upper West Side",
            "borough": "Manhattan",
            "price": 22000,
            "bedrooms": 3,
            "bathrooms": 3.5,
            "square_feet": 1882,
            "description": "Experience the ultimate in luxury living in this spectacular 3-bedroom, 3.5-bathroom penthouse-style residence spanning 1,882 sq ft. This trophy unit features soaring ceilings, wraparound windows, and premium finishes throughout. Each bedroom includes its own ensuite bathroom, plus a powder room for guests. The gourmet kitchen and expansive living areas are perfect for sophisticated entertaining. Enjoy exclusive access to The Waterline Club's unprecedented amenity collection.",
            "amenities": [
                "Exclusive Waterline Club membership included",
                "Private fitness training and wellness facilities",
                "Championship sports courts and simulator room", 
                "Luxury spa and aquatic center",
                "Multiple social and dining venues",
                "Private event and meeting spaces",
                "24/7 white-glove concierge service",
                "Valet and storage services",
                "Premium pet care facilities",
                "Landscaped outdoor terraces"
            ],
            "images": [
                "https://spcdn.shortpixel.ai/spio/ret_img,q_orig,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2025/08/floorplan-waterline-3-c3-542963.jpg",
                "https://spcdn.shortpixel.ai/spio/ret_img,q_orig,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/Interior_Kitchen_WaterlineSquare_Rental-wsq2-featured-4-1440x720-1.jpg"
            ],
            "available_date": datetime.utcnow(),
            "lease_terms": ["12 months", "24 months", "36 months"],
            "pet_policy": "Pet Friendly - Luxury pet amenities and concierge services",
            "parking": "Private parking and valet service included", 
            "utilities": "Heat, Hot Water, Gas included. Premium utility package available",
            "contact_info": {
                "name": "Chris Trunell", 
                "phone": "(646) 408-8048",
                "email": "placesnyc88@gmail.com"
            },
            "features": [
                "Penthouse-level finishes and views",
                "Three bedrooms with ensuite bathrooms", 
                "Powder room for guests",
                "Soaring ceilings throughout",
                "Wraparound floor-to-ceiling windows",
                "Gourmet kitchen with premium appliances",
                "Expansive living and dining areas",
                "Custom millwork and built-ins",
                "Private storage room"
            ],
            "transportation": [
                "Premium location near Columbus Circle (5 min walk)",
                "Lincoln Center and Broadway theaters (3 min walk)",
                "Central Park entrances nearby",
                "Easy access to all major transportation hubs"
            ],
            "is_no_fee": True,
            "created_at": datetime.utcnow(), 
            "updated_at": datetime.utcnow(),
            "property_management": "Windsor Communities",
            "building_year": 2019,
            "floor_plan": "3BR C3 Penthouse"
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Grand 4BR/3.5BA Family Residence - Waterline Square Premium",
            "address": "400 West 61st Street, Unit 2104, New York, NY 10023", 
            "neighborhood": "Upper West Side",
            "borough": "Manhattan",
            "price": 23552,
            "bedrooms": 4,
            "bathrooms": 3.5,
            "square_feet": 2149,
            "description": "This extraordinary 4-bedroom, 3.5-bathroom residence represents the pinnacle of luxury family living at Waterline Square. Spanning 2,149 sq ft, this grand home features four spacious bedrooms, multiple living areas, and a gourmet kitchen designed for both daily life and elegant entertaining. The master suite includes a walk-in closet and spa-like ensuite, while three additional bedrooms offer flexibility for family, guests, or home office space. Experience unparalleled luxury with full access to The Waterline Club.",
            "amenities": [
                "Complete Waterline Club lifestyle program", 
                "Family-friendly fitness and wellness facilities",
                "Children's programming and dedicated play areas",
                "Swimming instruction and aquatic programs",
                "Sports courts with professional instruction available",
                "Educational and creative studio programming",
                "Family social events and dining options",
                "Comprehensive concierge and family services", 
                "Pet care and training programs",
                "Private outdoor family spaces"
            ],
            "images": [
                "https://spcdn.shortpixel.ai/spio/ret_img,q_orig,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2025/08/floorplan-waterline-1-d1a-542872.jpg",
                "https://spcdn.shortpixel.ai/spio/ret_img,q_orig,to_webp,s_webp/www.windsorcommunities.com/wp-content/uploads/2022/03/Interior_Kitchen_WaterlineSquare_Rental-wsq2-featured-4-1440x720-1.jpg"
            ],
            "available_date": datetime.utcnow(),
            "lease_terms": ["12 months", "24 months", "36 months"],
            "pet_policy": "Pet Friendly - Family pet programs and comprehensive care",
            "parking": "Multiple parking spaces and storage options available",
            "utilities": "Heat, Hot Water, Gas included. Premium utility package", 
            "contact_info": {
                "name": "Chris Trunell",
                "phone": "(646) 408-8048", 
                "email": "placesnyc88@gmail.com"
            },
            "features": [
                "Four spacious bedrooms", 
                "3.5 bathrooms including powder room",
                "Master suite with walk-in closet and spa bath",
                "Multiple living and entertaining areas",
                "Gourmet kitchen with island and premium appliances",
                "Floor-to-ceiling windows throughout",
                "Custom storage solutions",
                "Premium finishes and fixtures", 
                "In-unit laundry and utility room"
            ],
            "transportation": [
                "Columbus Circle subway complex (4 min walk)",
                "Lincoln Center cultural district (3 min walk)",
                "Central Park West and multiple bus lines",
                "Convenient to all major NYC destinations"
            ],
            "is_no_fee": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(), 
            "property_management": "Windsor Communities",
            "building_year": 2019,
            "floor_plan": "4BR D1A Family"
        }
    ]
    
    # Insert all apartments into the database
    try:
        result = await db.apartments.insert_many(waterline_apartments)
        print(f"Successfully added {len(result.inserted_ids)} Waterline Square apartments to the database!")
        
        # Print summary of added apartments
        for apt in waterline_apartments:
            print(f"- {apt['bedrooms']}BR/{apt['bathrooms']}BA, {apt['square_feet']} sq ft, ${apt['price']:,}/month - {apt['title']}")
            
    except Exception as e:
        print(f"Error adding apartments: {e}")
        
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(add_waterline_square_apartments())