"""
AI-Powered Listing Moderation Service using Emergent LLM
Automates listing quality checks, categorization, and fraud detection
"""
import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

load_dotenv()

class ListingModerator:
    """AI-powered listing moderation and quality enhancement"""
    
    def __init__(self):
        self.api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
        
        # NYC neighborhoods and boroughs for validation
        self.nyc_boroughs = {
            'Manhattan': ['Upper West Side', 'Upper East Side', 'Midtown', 'Chelsea', 'Greenwich Village', 
                         'East Village', 'SoHo', 'TriBeCa', 'Financial District', 'Lower East Side',
                         'Harlem', 'Washington Heights', 'Inwood', "Hell's Kitchen", 'Murray Hill',
                         'Gramercy', 'Kips Bay', 'Yorkville', 'NoHo', 'Nolita', 'Battery Park City'],
            'Brooklyn': ['Williamsburg', 'DUMBO', 'Brooklyn Heights', 'Park Slope', 'Prospect Heights',
                        'Crown Heights', 'Bed-Stuy', 'Fort Greene', 'Boerum Hill', 'Carroll Gardens',
                        'Cobble Hill', 'Red Hook', 'Sunset Park', 'Bay Ridge', 'Bushwick',
                        'Greenpoint', 'East Flatbush', 'Flatbush', 'Prospect Lefferts Gardens'],
            'Queens': ['Astoria', 'Long Island City', 'Flushing', 'Forest Hills', 'Rego Park',
                      'Jackson Heights', 'Elmhurst', 'Corona', 'Sunnyside', 'Woodside',
                      'Ridgewood', 'Jamaica', 'Bayside', 'Fresh Meadows'],
            'Bronx': ['Mott Haven', 'South Bronx', 'Hunts Point', 'Fordham', 'Riverdale',
                     'Pelham Bay', 'Throggs Neck'],
            'Staten Island': ['St. George', 'Stapleton', 'Port Richmond', 'New Dorp']
        }
        
        # Price ranges for NYC by category (monthly rent)
        self.price_ranges = {
            'Budget Friendly': (1500, 2800),
            'Smart Value': (2800, 4500),
            'Sky\'s the Limit': (4500, 50000)
        }
    
    async def moderate_listing(self, listing: Dict) -> Dict:
        """
        Comprehensive AI moderation of a single listing
        Returns moderation results with scores and recommendations
        """
        try:
            # Initialize AI chat for this moderation session
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"moderate_{listing.get('id', 'unknown')}_{datetime.now().timestamp()}",
                system_message=self._get_moderation_system_message()
            ).with_model("openai", "gpt-4o-mini")
            
            # Prepare listing data for analysis
            listing_data = self._prepare_listing_for_analysis(listing)
            
            # Create moderation prompt
            prompt = self._create_moderation_prompt(listing_data)
            
            # Get AI analysis
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            # Parse AI response
            moderation_result = self._parse_moderation_response(response, listing)
            
            # Add additional checks
            moderation_result['neighborhood_check'] = self._verify_neighborhood_consistency(listing)
            moderation_result['price_anomaly'] = self._detect_price_anomaly(listing)
            moderation_result['duplicate_check'] = await self._check_duplicates(listing, chat)
            
            # Calculate final decision
            final_decision = self._calculate_final_decision(moderation_result)
            moderation_result['final_decision'] = final_decision
            moderation_result['moderation_timestamp'] = datetime.now().isoformat()
            
            return moderation_result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'final_decision': 'manual_review',
                'reason': f'Moderation failed: {str(e)}'
            }
    
    def _get_moderation_system_message(self) -> str:
        """System message for AI moderator"""
        return """You are an expert real estate listing moderator for NoFeePlaces.com, a NYC no-fee apartment platform.

Your responsibilities:
1. Assess content quality (descriptions, titles, completeness)
2. Evaluate image quality and relevance
3. Detect spam, scams, and fraudulent listings
4. Categorize listings (Budget Friendly: $1500-$2800, Smart Value: $2800-$4500, Sky's the Limit: $4500+)
5. Identify suspicious patterns or red flags

Respond in JSON format with:
{
  "content_quality_score": 0-100,
  "content_issues": ["issue1", "issue2"],
  "spam_probability": 0-100,
  "spam_indicators": ["indicator1", "indicator2"],
  "image_quality_score": 0-100,
  "image_issues": ["issue1", "issue2"],
  "recommended_category": "Budget Friendly|Smart Value|Sky's the Limit",
  "category_reasoning": "explanation",
  "red_flags": ["flag1", "flag2"],
  "recommendation": "approve|reject|manual_review",
  "confidence": 0-100,
  "summary": "brief explanation"
}

Be thorough but fair. Approve legitimate listings, reject obvious scams, flag borderline cases for manual review."""
    
    def _prepare_listing_for_analysis(self, listing: Dict) -> Dict:
        """Prepare listing data for AI analysis"""
        return {
            'title': listing.get('title', ''),
            'description': listing.get('description', ''),
            'price': listing.get('price', 0),
            'bedrooms': listing.get('bedrooms', 0),
            'bathrooms': listing.get('bathrooms', 0),
            'sqft': listing.get('sqft'),
            'address': listing.get('address', ''),
            'neighborhood': listing.get('neighborhood', ''),
            'borough': listing.get('borough', ''),
            'amenities': listing.get('amenities', []),
            'images_count': len(listing.get('images', [])),
            'images': listing.get('images', [])[:3],  # First 3 images
            'contact_info': listing.get('contact_info', {}),
            'broker_fee': listing.get('broker_fee', True),
            'available_date': listing.get('available_date', '')
        }
    
    def _create_moderation_prompt(self, listing_data: Dict) -> str:
        """Create detailed moderation prompt"""
        return f"""Analyze this NYC apartment listing for quality, legitimacy, and proper categorization:

**LISTING DETAILS:**
Title: {listing_data['title']}
Description: {listing_data['description'][:500]}...
Price: ${listing_data['price']}/month
Bedrooms: {listing_data['bedrooms']} | Bathrooms: {listing_data['bathrooms']} | Sqft: {listing_data['sqft']}
Location: {listing_data['neighborhood']}, {listing_data['borough']}
Address: {listing_data['address']}
Amenities: {', '.join(listing_data['amenities'][:10])}
Images: {listing_data['images_count']} images provided
Broker Fee: {listing_data['broker_fee']}
Available: {listing_data['available_date']}

**YOUR ANALYSIS:**
1. Content Quality: Is the description clear, detailed, and professional?
2. Spam Detection: Any signs of scams, fake listings, or suspicious patterns?
3. Image Quality: Are images relevant apartment photos (not stock images or unrelated)?
4. Price Categorization: Based on ${listing_data['price']}/month and features, which category?
   - Budget Friendly: $1500-$2800
   - Smart Value: $2800-$4500
   - Sky's the Limit: $4500+
5. Red Flags: Missing info, unrealistic prices, suspicious contact details?

Provide your analysis in the specified JSON format."""
    
    def _parse_moderation_response(self, response: str, listing: Dict) -> Dict:
        """Parse AI response into structured moderation result"""
        try:
            # Try to extract JSON from response
            if '{' in response and '}' in response:
                start = response.index('{')
                end = response.rindex('}') + 1
                json_str = response[start:end]
                result = json.loads(json_str)
                result['success'] = True
                result['ai_analysis_raw'] = response
                return result
            else:
                # Fallback if JSON parsing fails
                return {
                    'success': False,
                    'content_quality_score': 50,
                    'spam_probability': 50,
                    'image_quality_score': 50,
                    'recommendation': 'manual_review',
                    'confidence': 30,
                    'summary': 'Unable to parse AI response',
                    'ai_analysis_raw': response
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to parse AI response: {str(e)}',
                'recommendation': 'manual_review',
                'ai_analysis_raw': response
            }
    
    def _verify_neighborhood_consistency(self, listing: Dict) -> Dict:
        """Verify neighborhood and borough are consistent"""
        neighborhood = listing.get('neighborhood', '')
        borough = listing.get('borough', '')
        
        if not neighborhood or not borough:
            return {
                'consistent': False,
                'issue': 'Missing neighborhood or borough',
                'severity': 'high'
            }
        
        # Check if neighborhood is known for this borough
        valid_neighborhoods = self.nyc_boroughs.get(borough, [])
        
        # Fuzzy match (case insensitive, partial match)
        neighborhood_found = any(
            neighborhood.lower() in valid.lower() or valid.lower() in neighborhood.lower()
            for valid in valid_neighborhoods
        )
        
        if not neighborhood_found and valid_neighborhoods:
            return {
                'consistent': False,
                'issue': f'{neighborhood} not typically associated with {borough}',
                'severity': 'medium',
                'suggestion': f'Common {borough} neighborhoods: {", ".join(valid_neighborhoods[:5])}'
            }
        
        return {
            'consistent': True,
            'message': f'{neighborhood}, {borough} is valid'
        }
    
    def _detect_price_anomaly(self, listing: Dict) -> Dict:
        """Detect price anomalies based on location and size"""
        price = listing.get('price', 0)
        bedrooms = listing.get('bedrooms', 0)
        borough = listing.get('borough', '')
        
        if price <= 0:
            return {
                'anomaly': True,
                'issue': 'Price must be greater than 0',
                'severity': 'critical'
            }
        
        # Extremely low prices (likely scam)
        if price < 1000:
            return {
                'anomaly': True,
                'issue': f'${price}/month is unrealistically low for NYC',
                'severity': 'critical',
                'recommendation': 'Likely scam - reject'
            }
        
        # Manhattan premium pricing expectations
        if borough == 'Manhattan':
            if bedrooms >= 2 and price < 3000:
                return {
                    'anomaly': True,
                    'issue': f'${price}/month for {bedrooms}BR in Manhattan is unusually low',
                    'severity': 'high',
                    'recommendation': 'Verify pricing'
                }
        
        # Extremely high prices
        if price > 20000 and bedrooms <= 2:
            return {
                'anomaly': True,
                'issue': f'${price}/month for {bedrooms}BR seems unusually high',
                'severity': 'medium',
                'recommendation': 'Verify luxury features justify price'
            }
        
        return {
            'anomaly': False,
            'message': f'${price}/month for {bedrooms}BR in {borough} is within normal range'
        }
    
    async def _check_duplicates(self, listing: Dict, chat: LlmChat) -> Dict:
        """Use AI to detect potential duplicate listings"""
        try:
            # Create duplicate detection prompt
            prompt = f"""Based on this listing information, assess the likelihood this is a duplicate:

Address: {listing.get('address', 'Not provided')}
Title: {listing.get('title', '')}
Price: ${listing.get('price', 0)}
Bedrooms: {listing.get('bedrooms', 0)}
Neighborhood: {listing.get('neighborhood', '')}, {listing.get('borough', '')}

Consider:
1. If address is generic or missing (higher duplicate risk)
2. If title is very generic (e.g., "Nice Apartment")
3. If images appear to be stock photos

Respond with JSON:
{{
  "duplicate_probability": 0-100,
  "reasoning": "explanation",
  "recommendation": "likely_unique|possible_duplicate|likely_duplicate"
}}"""
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            # Parse response
            if '{' in response and '}' in response:
                start = response.index('{')
                end = response.rindex('}') + 1
                result = json.loads(response[start:end])
                return result
            
            return {
                'duplicate_probability': 30,
                'reasoning': 'Unable to analyze',
                'recommendation': 'possible_duplicate'
            }
            
        except Exception as e:
            return {
                'duplicate_probability': 50,
                'reasoning': f'Check failed: {str(e)}',
                'recommendation': 'manual_review'
            }
    
    def _calculate_final_decision(self, moderation_result: Dict) -> Dict:
        """Calculate final moderation decision based on all checks"""
        
        # Extract scores
        content_score = moderation_result.get('content_quality_score', 50)
        spam_prob = moderation_result.get('spam_probability', 50)
        image_score = moderation_result.get('image_quality_score', 50)
        confidence = moderation_result.get('confidence', 50)
        
        ai_recommendation = moderation_result.get('recommendation', 'manual_review')
        
        # Check for critical failures
        price_anomaly = moderation_result.get('price_anomaly', {})
        if price_anomaly.get('severity') == 'critical':
            return {
                'action': 'reject',
                'reason': price_anomaly.get('issue'),
                'confidence': 95
            }
        
        neighborhood_check = moderation_result.get('neighborhood_check', {})
        if not neighborhood_check.get('consistent') and neighborhood_check.get('severity') == 'high':
            return {
                'action': 'manual_review',
                'reason': neighborhood_check.get('issue'),
                'confidence': 70
            }
        
        # High spam probability - reject
        if spam_prob > 70:
            return {
                'action': 'reject',
                'reason': f'High spam probability ({spam_prob}%)',
                'confidence': confidence
            }
        
        # Low quality content - manual review
        if content_score < 40 or image_score < 40:
            return {
                'action': 'manual_review',
                'reason': f'Quality concerns (content: {content_score}%, images: {image_score}%)',
                'confidence': confidence
            }
        
        # AI recommends rejection
        if ai_recommendation == 'reject':
            return {
                'action': 'reject',
                'reason': moderation_result.get('summary', 'AI recommendation: reject'),
                'confidence': confidence
            }
        
        # High quality, low spam - auto approve
        if content_score >= 70 and spam_prob < 30 and image_score >= 60 and ai_recommendation == 'approve':
            return {
                'action': 'approve',
                'reason': f'High quality listing (content: {content_score}%, spam: {spam_prob}%, images: {image_score}%)',
                'confidence': confidence,
                'auto_approved': True
            }
        
        # Default to manual review for borderline cases
        return {
            'action': 'manual_review',
            'reason': f'Borderline case requiring human review (AI: {ai_recommendation})',
            'confidence': confidence
        }
    
    async def moderate_batch(self, listings: List[Dict]) -> Dict:
        """Moderate multiple listings in batch"""
        results = {
            'total': len(listings),
            'approved': 0,
            'rejected': 0,
            'manual_review': 0,
            'failed': 0,
            'listings': []
        }
        
        for listing in listings:
            try:
                moderation = await self.moderate_listing(listing)
                decision = moderation.get('final_decision', {}).get('action', 'manual_review')
                
                if decision == 'approve':
                    results['approved'] += 1
                elif decision == 'reject':
                    results['rejected'] += 1
                else:
                    results['manual_review'] += 1
                
                results['listings'].append({
                    'listing_id': listing.get('id'),
                    'title': listing.get('title'),
                    'decision': decision,
                    'moderation': moderation
                })
                
            except Exception as e:
                results['failed'] += 1
                results['listings'].append({
                    'listing_id': listing.get('id'),
                    'title': listing.get('title'),
                    'decision': 'failed',
                    'error': str(e)
                })
        
        return results
