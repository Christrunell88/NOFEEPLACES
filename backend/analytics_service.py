"""
Simple Analytics Service for NoFeePlaces.com
Tracks visitors, page views, and provides basic analytics without relying on external services
"""

import asyncio
import os
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import hashlib

load_dotenv()

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/nofeeplaces')

class AnalyticsService:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db_name = os.environ.get('DB_NAME', 'nofeeplaces')
        self.db = self.client[self.db_name]
        
    async def track_visitor(self, visitor_data: Dict[str, Any]) -> bool:
        """Track a new visitor session"""
        try:
            # Create visitor record
            visitor_record = {
                "session_id": visitor_data.get('sessionId'),
                "page": visitor_data.get('page', '/'),
                "referrer": visitor_data.get('referrer', 'direct'),
                "user_agent": visitor_data.get('userAgent', ''),
                "fingerprint": visitor_data.get('fingerprint', ''),
                "timestamp": datetime.now(timezone.utc),
                "ip_hash": self._hash_ip(visitor_data.get('ip', 'unknown')),
                "is_unique": await self._is_unique_visitor(visitor_data),
                "browser_info": self._parse_user_agent(visitor_data.get('userAgent', '')),
                "page_load_time": visitor_data.get('loadTime'),
                "viewport": visitor_data.get('viewport'),
                "referrer_domain": self._extract_domain(visitor_data.get('referrer', ''))
            }
            
            # Insert visitor record
            result = await self.db.visitor_analytics.insert_one(visitor_record)
            
            # Update daily stats
            await self._update_daily_stats(visitor_record)
            
            # Update page stats
            await self._update_page_stats(visitor_record)
            
            return bool(result.inserted_id)
            
        except Exception as e:
            print(f"Error tracking visitor: {str(e)}")
            return False
    
    async def get_analytics_stats(self) -> Dict[str, Any]:
        """Get comprehensive analytics statistics"""
        try:
            now = datetime.now(timezone.utc)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=7)
            
            # Today's visitors
            today_visitors = await self.db.visitor_analytics.count_documents({
                "timestamp": {"$gte": today_start}
            })
            
            # Today's unique visitors
            today_unique = await self.db.visitor_analytics.count_documents({
                "timestamp": {"$gte": today_start},
                "is_unique": True
            })
            
            # Total visitors
            total_visitors = await self.db.visitor_analytics.count_documents({})
            
            # Current online (last 5 minutes)
            online_threshold = now - timedelta(minutes=5)
            current_online = await self.db.visitor_analytics.count_documents({
                "timestamp": {"$gte": online_threshold}
            })
            
            # Top pages today
            top_pages_pipeline = [
                {"$match": {"timestamp": {"$gte": today_start}}},
                {"$group": {"_id": "$page", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10},
                {"$project": {"page": "$_id", "count": 1, "_id": 0}}
            ]
            top_pages = await self.db.visitor_analytics.aggregate(top_pages_pipeline).to_list(length=10)
            
            # Recent visitors (last 10)
            recent_visitors_cursor = self.db.visitor_analytics.find(
                {}, 
                {"timestamp": 1, "page": 1, "referrer_domain": 1, "browser_info": 1}
            ).sort("timestamp", -1).limit(10)
            recent_visitors = await recent_visitors_cursor.to_list(length=10)
            
            # Weekly trend
            weekly_stats = await self._get_weekly_trend(week_start)
            
            # Traffic sources
            traffic_sources = await self._get_traffic_sources(today_start)
            
            # Browser stats
            browser_stats = await self._get_browser_stats(today_start)
            
            return {
                "todayVisitors": today_visitors,
                "todayUniqueVisitors": today_unique,
                "totalVisitors": total_visitors,
                "currentOnline": current_online,
                "topPages": top_pages,
                "recentVisitors": [
                    {
                        "timestamp": visitor["timestamp"].isoformat(),
                        "page": visitor.get("page", "/"),
                        "referrer": visitor.get("referrer_domain", "direct"),
                        "browser": visitor.get("browser_info", {}).get("browser", "unknown")
                    }
                    for visitor in recent_visitors
                ],
                "weeklyTrend": weekly_stats,
                "trafficSources": traffic_sources,
                "browserStats": browser_stats,
                "last_updated": now.isoformat()
            }
            
        except Exception as e:
            print(f"Error getting analytics stats: {str(e)}")
            return {
                "todayVisitors": 0,
                "totalVisitors": 0,
                "currentOnline": 0,
                "topPages": [],
                "recentVisitors": [],
                "error": str(e)
            }
    
    async def _is_unique_visitor(self, visitor_data: Dict[str, Any]) -> bool:
        """Check if this is a unique visitor today"""
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        fingerprint = visitor_data.get('fingerprint', '')
        
        if not fingerprint:
            return True  # Assume unique if no fingerprint
        
        existing = await self.db.visitor_analytics.find_one({
            "fingerprint": fingerprint,
            "timestamp": {"$gte": today_start}
        })
        
        return existing is None
    
    def _hash_ip(self, ip: str) -> str:
        """Hash IP address for privacy"""
        return hashlib.sha256(f"{ip}_nofeeplaces_salt".encode()).hexdigest()[:16]
    
    def _parse_user_agent(self, user_agent: str) -> Dict[str, str]:
        """Parse user agent string"""
        ua = user_agent.lower()
        
        # Browser detection
        if 'chrome' in ua and 'edg' not in ua:
            browser = 'Chrome'
        elif 'firefox' in ua:
            browser = 'Firefox'
        elif 'safari' in ua and 'chrome' not in ua:
            browser = 'Safari'
        elif 'edg' in ua:
            browser = 'Edge'
        else:
            browser = 'Other'
        
        # OS detection
        if 'windows' in ua:
            os = 'Windows'
        elif 'mac' in ua:
            os = 'macOS'
        elif 'linux' in ua:
            os = 'Linux'
        elif 'android' in ua:
            os = 'Android'
        elif 'iphone' in ua or 'ipad' in ua:
            os = 'iOS'
        else:
            os = 'Other'
        
        # Device type
        if 'mobile' in ua or 'android' in ua or 'iphone' in ua:
            device = 'Mobile'
        elif 'tablet' in ua or 'ipad' in ua:
            device = 'Tablet'
        else:
            device = 'Desktop'
        
        return {
            "browser": browser,
            "os": os,
            "device": device,
            "raw": user_agent[:100]  # Truncate for storage
        }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        if not url or url == 'direct':
            return 'direct'
        
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return domain if domain else 'unknown'
        except:
            return 'unknown'
    
    async def _update_daily_stats(self, visitor_record: Dict[str, Any]):
        """Update daily aggregated stats"""
        date_key = visitor_record["timestamp"].date().isoformat()
        
        await self.db.daily_stats.update_one(
            {"date": date_key},
            {
                "$inc": {
                    "total_visits": 1,
                    "unique_visits": 1 if visitor_record["is_unique"] else 0
                },
                "$setOnInsert": {"created_at": datetime.now(timezone.utc)}
            },
            upsert=True
        )
    
    async def _update_page_stats(self, visitor_record: Dict[str, Any]):
        """Update page-level stats"""
        date_key = visitor_record["timestamp"].date().isoformat()
        page = visitor_record["page"]
        
        await self.db.page_stats.update_one(
            {"date": date_key, "page": page},
            {
                "$inc": {"visits": 1},
                "$setOnInsert": {"created_at": datetime.now(timezone.utc)}
            },
            upsert=True
        )
    
    async def _get_weekly_trend(self, week_start: datetime) -> List[Dict[str, Any]]:
        """Get weekly visitor trend"""
        try:
            pipeline = [
                {"$match": {"timestamp": {"$gte": week_start}}},
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$timestamp"
                            }
                        },
                        "visits": {"$sum": 1},
                        "unique_visits": {
                            "$sum": {"$cond": [{"$eq": ["$is_unique", True]}, 1, 0]}
                        }
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            results = await self.db.visitor_analytics.aggregate(pipeline).to_list(length=7)
            return [
                {
                    "date": result["_id"],
                    "visits": result["visits"],
                    "unique_visits": result["unique_visits"]
                }
                for result in results
            ]
        except Exception as e:
            print(f"Error getting weekly trend: {str(e)}")
            return []
    
    async def _get_traffic_sources(self, today_start: datetime) -> List[Dict[str, Any]]:
        """Get traffic sources for today"""
        try:
            pipeline = [
                {"$match": {"timestamp": {"$gte": today_start}}},
                {"$group": {"_id": "$referrer_domain", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10},
                {"$project": {"source": "$_id", "count": 1, "_id": 0}}
            ]
            
            return await self.db.visitor_analytics.aggregate(pipeline).to_list(length=10)
        except Exception as e:
            print(f"Error getting traffic sources: {str(e)}")
            return []
    
    async def _get_browser_stats(self, today_start: datetime) -> List[Dict[str, Any]]:
        """Get browser stats for today"""
        try:
            pipeline = [
                {"$match": {"timestamp": {"$gte": today_start}}},
                {"$group": {"_id": "$browser_info.browser", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10},
                {"$project": {"browser": "$_id", "count": 1, "_id": 0}}
            ]
            
            return await self.db.visitor_analytics.aggregate(pipeline).to_list(length=10)
        except Exception as e:
            print(f"Error getting browser stats: {str(e)}")
            return []

# Global analytics service instance
analytics_service = AnalyticsService()