"""
Optimized Insight Store
Codename: "Lightning Retrieval Engine"

High-performance, robust data store optimized for instant insight retrieval
with intelligent caching, indexing, and compression.
"""

import os
import json
import sqlite3
import hashlib
import time
import threading
import pickle
import gzip
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
DATA_DIR = "data/optimized_store"
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "insights.db")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
INDEX_DIR = os.path.join(DATA_DIR, "indexes")

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)

# Performance settings
CACHE_TTL = 3600  # 1 hour cache TTL
MAX_CACHE_SIZE = 1000  # Maximum cached items
BATCH_SIZE = 1000  # Batch size for bulk operations
COMPRESSION_THRESHOLD = 1024  # Compress data larger than 1KB


class OptimizedInsightStore:
    """
    High-performance insight storage and retrieval system with:
    - SQLite backend with optimized indexes
    - In-memory LRU cache
    - Compressed storage for large payloads
    - Real-time indexing for fast queries
    - Batch operations for bulk processing
    """
    
    def __init__(self):
        """Initialize the optimized insight store."""
        self.db_path = DB_PATH
        self.cache = {}
        self.cache_timestamps = {}
        self.indexes = {
            "domain": defaultdict(list),
            "category": defaultdict(list),
            "agent": defaultdict(list),
            "quality": defaultdict(list),
            "timestamp": []
        }
        
        # Thread lock for cache safety
        self.cache_lock = threading.Lock()
        
        # Initialize database
        self._init_database()
        
        # Load indexes
        self._load_indexes()
        
        logger.info("🚀 OPTIMIZED INSIGHT STORE INITIALIZED - Lightning fast retrieval ready!")
        
    def _init_database(self):
        """Initialize SQLite database with optimized schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create insights table with optimized structure
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insights (
                id TEXT PRIMARY KEY,
                domain TEXT NOT NULL,
                category TEXT,
                agent_name TEXT,
                insight_type TEXT,
                quality_score REAL,
                engagement_score REAL,
                timestamp INTEGER,
                raw_data BLOB,
                compressed INTEGER DEFAULT 0,
                INDEX(domain),
                INDEX(category),
                INDEX(agent_name),
                INDEX(quality_score),
                INDEX(timestamp),
                INDEX(domain, timestamp),
                INDEX(category, quality_score)
            )
        """)
        
        # Create engagement metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS engagement_metrics (
                insight_id TEXT,
                click_rate REAL,
                retention_time REAL,
                share_rate REAL,
                requery_rate REAL,
                total_impressions INTEGER,
                last_updated INTEGER,
                FOREIGN KEY(insight_id) REFERENCES insights(id),
                INDEX(insight_id),
                INDEX(click_rate),
                INDEX(retention_time)
            )
        """)
        
        # Create agent performance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_performance (
                agent_name TEXT PRIMARY KEY,
                total_insights INTEGER DEFAULT 0,
                avg_quality REAL DEFAULT 0.0,
                avg_engagement REAL DEFAULT 0.0,
                last_active INTEGER,
                status TEXT DEFAULT 'active',
                INDEX(avg_quality),
                INDEX(avg_engagement),
                INDEX(last_active)
            )
        """)
        
        # Create composite indexes for complex queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_domain_quality_time ON insights(domain, quality_score, timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category_engagement ON insights(category, engagement_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent_quality ON insights(agent_name, quality_score)")
        
        conn.commit()
        conn.close()
        
        logger.info("Database initialized with optimized indexes")
        
    def _load_indexes(self):
        """Load in-memory indexes for ultra-fast lookups."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Load domain index
            cursor.execute("SELECT id, domain FROM insights")
            for insight_id, domain in cursor.fetchall():
                self.indexes["domain"][domain].append(insight_id)
                
            # Load category index
            cursor.execute("SELECT id, category FROM insights WHERE category IS NOT NULL")
            for insight_id, category in cursor.fetchall():
                self.indexes["category"][category].append(insight_id)
                
            # Load agent index
            cursor.execute("SELECT id, agent_name FROM insights WHERE agent_name IS NOT NULL")
            for insight_id, agent_name in cursor.fetchall():
                self.indexes["agent"][agent_name].append(insight_id)
                
            # Load quality index (bucketed)
            cursor.execute("SELECT id, quality_score FROM insights WHERE quality_score IS NOT NULL")
            for insight_id, quality_score in cursor.fetchall():
                quality_bucket = int(quality_score * 10) / 10  # Bucket by 0.1
                self.indexes["quality"][quality_bucket].append(insight_id)
                
            # Load timestamp index (sorted)
            cursor.execute("SELECT id, timestamp FROM insights ORDER BY timestamp DESC")
            self.indexes["timestamp"] = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            logger.info(f"Loaded indexes: {len(self.indexes['domain'])} domains, {len(self.indexes['category'])} categories")
            
        except Exception as e:
            logger.error(f"Error loading indexes: {e}")
            
    def _compress_data(self, data: Any) -> Tuple[bytes, bool]:
        """Compress data if it's large enough to benefit."""
        pickled_data = pickle.dumps(data)
        
        if len(pickled_data) > COMPRESSION_THRESHOLD:
            compressed_data = gzip.compress(pickled_data)
            return compressed_data, True
        else:
            return pickled_data, False
            
    def _decompress_data(self, data: bytes, is_compressed: bool) -> Any:
        """Decompress data if needed."""
        if is_compressed:
            decompressed_data = gzip.decompress(data)
            return pickle.loads(decompressed_data)
        else:
            return pickle.loads(data)
            
    def _get_cache_key(self, query_type: str, **kwargs) -> str:
        """Generate cache key for query."""
        key_parts = [query_type]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        return hashlib.md5("|".join(key_parts).encode()).hexdigest()
        
    def _cache_get(self, cache_key: str) -> Optional[Any]:
        """Get item from cache if valid."""
        with self.cache_lock:
            if cache_key in self.cache:
                timestamp = self.cache_timestamps.get(cache_key, 0)
                if time.time() - timestamp < CACHE_TTL:
                    return self.cache[cache_key]
                else:
                    # Expired, remove from cache
                    del self.cache[cache_key]
                    del self.cache_timestamps[cache_key]
        return None
        
    def _cache_set(self, cache_key: str, data: Any):
        """Set item in cache with TTL."""
        with self.cache_lock:
            # Evict oldest items if cache is full
            if len(self.cache) >= MAX_CACHE_SIZE:
                oldest_key = min(self.cache_timestamps.keys(), 
                               key=lambda k: self.cache_timestamps[k])
                del self.cache[oldest_key]
                del self.cache_timestamps[oldest_key]
                
            self.cache[cache_key] = data
            self.cache_timestamps[cache_key] = time.time()
            
    def store_insight(self, insight_data: Dict) -> str:
        """
        Store insight with optimized compression and indexing.
        
        Args:
            insight_data: Insight data dictionary
            
        Returns:
            Insight ID
        """
        insight_id = insight_data.get("id", f"insight_{int(time.time() * 1000)}")
        domain = insight_data.get("domain", "")
        category = insight_data.get("category")
        agent_name = insight_data.get("agent_name")
        insight_type = insight_data.get("type")
        quality_score = insight_data.get("quality_score", 0.0)
        engagement_score = insight_data.get("engagement_score", 0.0)
        timestamp = int(insight_data.get("timestamp", time.time()))
        
        # Compress raw data
        raw_data, is_compressed = self._compress_data(insight_data)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert insight
            cursor.execute("""
                INSERT OR REPLACE INTO insights 
                (id, domain, category, agent_name, insight_type, quality_score, engagement_score, timestamp, raw_data, compressed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (insight_id, domain, category, agent_name, insight_type, quality_score, engagement_score, timestamp, raw_data, int(is_compressed)))
            
            # Update agent performance
            cursor.execute("""
                INSERT OR REPLACE INTO agent_performance 
                (agent_name, total_insights, avg_quality, avg_engagement, last_active)
                VALUES (?, 
                    COALESCE((SELECT total_insights FROM agent_performance WHERE agent_name = ?) + 1, 1),
                    COALESCE((SELECT avg_quality FROM agent_performance WHERE agent_name = ? * 0.9 + ? * 0.1), ?),
                    COALESCE((SELECT avg_engagement FROM agent_performance WHERE agent_name = ? * 0.9 + ? * 0.1), ?),
                    ?)
            """, (agent_name, agent_name, agent_name, quality_score, quality_score, agent_name, engagement_score, engagement_score, timestamp))
            
            conn.commit()
            
            # Update in-memory indexes
            self.indexes["domain"][domain].append(insight_id)
            if category:
                self.indexes["category"][category].append(insight_id)
            if agent_name:
                self.indexes["agent"][agent_name].append(insight_id)
                
            quality_bucket = int(quality_score * 10) / 10
            self.indexes["quality"][quality_bucket].append(insight_id)
            
            # Insert into timestamp index (maintain sorted order)
            self.indexes["timestamp"].insert(0, insight_id)
            if len(self.indexes["timestamp"]) > 10000:  # Limit timestamp index size
                self.indexes["timestamp"] = self.indexes["timestamp"][:10000]
                
            # Clear relevant caches
            self._invalidate_cache_for_domain(domain)
            
            logger.info(f"Stored insight {insight_id} for {domain} (compressed: {is_compressed})")
            return insight_id
            
        except Exception as e:
            logger.error(f"Error storing insight: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
            
    def get_insights_by_domain(self, domain: str, limit: int = 100, include_engagement: bool = True) -> List[Dict]:
        """
        Ultra-fast domain insight retrieval using indexes and caching.
        
        Args:
            domain: Domain name
            limit: Maximum number of insights
            include_engagement: Whether to include engagement metrics
            
        Returns:
            List of insights
        """
        cache_key = self._get_cache_key("domain", domain=domain, limit=limit, engagement=include_engagement)
        
        # Check cache first
        cached_result = self._cache_get(cache_key)
        if cached_result is not None:
            return cached_result
            
        # Use index for fast lookup
        insight_ids = self.indexes["domain"].get(domain, [])
        
        if not insight_ids:
            return []
            
        # Limit results
        insight_ids = insight_ids[:limit]
        
        # Fetch insights in batch
        insights = self._fetch_insights_batch(insight_ids, include_engagement)
        
        # Cache results
        self._cache_set(cache_key, insights)
        
        return insights
        
    def get_insights_by_quality_range(self, min_quality: float, max_quality: float = 1.0, limit: int = 100) -> List[Dict]:
        """
        Get insights within quality score range.
        
        Args:
            min_quality: Minimum quality score
            max_quality: Maximum quality score
            limit: Maximum number of insights
            
        Returns:
            List of insights
        """
        cache_key = self._get_cache_key("quality_range", min_q=min_quality, max_q=max_quality, limit=limit)
        
        cached_result = self._cache_get(cache_key)
        if cached_result is not None:
            return cached_result
            
        # Find relevant quality buckets
        insight_ids = []
        
        for quality_bucket, ids in self.indexes["quality"].items():
            if min_quality <= quality_bucket <= max_quality:
                insight_ids.extend(ids)
                
        # Sort by quality (highest first) and limit
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if insight_ids:
            placeholders = ",".join("?" * len(insight_ids))
            cursor.execute(f"""
                SELECT id FROM insights 
                WHERE id IN ({placeholders}) AND quality_score BETWEEN ? AND ?
                ORDER BY quality_score DESC, timestamp DESC
                LIMIT ?
            """, insight_ids + [min_quality, max_quality, limit])
            
            sorted_ids = [row[0] for row in cursor.fetchall()]
        else:
            sorted_ids = []
            
        conn.close()
        
        insights = self._fetch_insights_batch(sorted_ids, include_engagement=True)
        
        self._cache_set(cache_key, insights)
        return insights
        
    def get_recent_insights(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """
        Get recent insights using optimized timestamp index.
        
        Args:
            hours: Number of hours to look back
            limit: Maximum number of insights
            
        Returns:
            List of recent insights
        """
        cache_key = self._get_cache_key("recent", hours=hours, limit=limit)
        
        cached_result = self._cache_get(cache_key)
        if cached_result is not None:
            return cached_result
            
        cutoff_time = int(time.time() - (hours * 3600))
        
        # Use pre-sorted timestamp index for ultra-fast retrieval
        recent_ids = []
        for insight_id in self.indexes["timestamp"]:
            if len(recent_ids) >= limit:
                break
                
            # Quick timestamp check using database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp FROM insights WHERE id = ?", (insight_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result and result[0] >= cutoff_time:
                recent_ids.append(insight_id)
                
        insights = self._fetch_insights_batch(recent_ids, include_engagement=True)
        
        self._cache_set(cache_key, insights)
        return insights
        
    def get_agent_insights(self, agent_name: str, limit: int = 100) -> List[Dict]:
        """
        Get insights by agent with performance metrics.
        
        Args:
            agent_name: Agent name
            limit: Maximum number of insights
            
        Returns:
            List of insights with agent performance
        """
        cache_key = self._get_cache_key("agent", agent=agent_name, limit=limit)
        
        cached_result = self._cache_get(cache_key)
        if cached_result is not None:
            return cached_result
            
        # Use agent index
        insight_ids = self.indexes["agent"].get(agent_name, [])[:limit]
        insights = self._fetch_insights_batch(insight_ids, include_engagement=True)
        
        # Add agent performance metrics
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agent_performance WHERE agent_name = ?", (agent_name,))
        agent_perf = cursor.fetchone()
        conn.close()
        
        for insight in insights:
            insight["agent_performance"] = {
                "total_insights": agent_perf[1] if agent_perf else 0,
                "avg_quality": agent_perf[2] if agent_perf else 0.0,
                "avg_engagement": agent_perf[3] if agent_perf else 0.0,
                "status": agent_perf[5] if agent_perf else "unknown"
            }
            
        self._cache_set(cache_key, insights)
        return insights
        
    def _fetch_insights_batch(self, insight_ids: List[str], include_engagement: bool = True) -> List[Dict]:
        """
        Efficiently fetch multiple insights in a single query.
        
        Args:
            insight_ids: List of insight IDs
            include_engagement: Whether to include engagement metrics
            
        Returns:
            List of insight dictionaries
        """
        if not insight_ids:
            return []
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        placeholders = ",".join("?" * len(insight_ids))
        
        if include_engagement:
            # Join with engagement metrics
            cursor.execute(f"""
                SELECT i.*, e.click_rate, e.retention_time, e.share_rate, e.requery_rate, e.total_impressions
                FROM insights i
                LEFT JOIN engagement_metrics e ON i.id = e.insight_id
                WHERE i.id IN ({placeholders})
                ORDER BY i.timestamp DESC
            """, insight_ids)
        else:
            cursor.execute(f"""
                SELECT * FROM insights 
                WHERE id IN ({placeholders})
                ORDER BY timestamp DESC
            """, insight_ids)
            
        results = cursor.fetchall()
        conn.close()
        
        insights = []
        for row in results:
            # Decompress raw data
            raw_data = self._decompress_data(row[8], bool(row[9]))
            
            insight = raw_data.copy()
            insight.update({
                "id": row[0],
                "domain": row[1],
                "category": row[2],
                "agent_name": row[3],
                "insight_type": row[4],
                "quality_score": row[5],
                "engagement_score": row[6],
                "timestamp": row[7]
            })
            
            # Add engagement metrics if available
            if include_engagement and len(row) > 10:
                insight["engagement_metrics"] = {
                    "click_rate": row[10],
                    "retention_time": row[11],
                    "share_rate": row[12],
                    "requery_rate": row[13],
                    "total_impressions": row[14]
                }
                
            insights.append(insight)
            
        return insights
        
    def _invalidate_cache_for_domain(self, domain: str):
        """Invalidate cache entries related to a domain."""
        with self.cache_lock:
            keys_to_remove = [k for k in self.cache.keys() if f"domain:{domain}" in k]
            for key in keys_to_remove:
                del self.cache[key]
                del self.cache_timestamps[key]
                
    def search_insights(self, query: str, filters: Dict = None, limit: int = 50) -> List[Dict]:
        """
        Advanced insight search with filters and full-text capabilities.
        
        Args:
            query: Search query
            filters: Additional filters (domain, category, agent, quality_range, etc.)
            limit: Maximum results
            
        Returns:
            List of matching insights
        """
        filters = filters or {}
        cache_key = self._get_cache_key("search", query=query, filters=str(filters), limit=limit)
        
        cached_result = self._cache_get(cache_key)
        if cached_result is not None:
            return cached_result
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build dynamic query
        where_conditions = []
        params = []
        
        # Text search in raw data (simplified - could be enhanced with FTS)
        if query:
            where_conditions.append("(domain LIKE ? OR category LIKE ? OR insight_type LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
            
        # Apply filters
        if filters.get("domain"):
            where_conditions.append("domain = ?")
            params.append(filters["domain"])
            
        if filters.get("category"):
            where_conditions.append("category = ?")
            params.append(filters["category"])
            
        if filters.get("agent"):
            where_conditions.append("agent_name = ?")
            params.append(filters["agent"])
            
        if filters.get("min_quality"):
            where_conditions.append("quality_score >= ?")
            params.append(filters["min_quality"])
            
        if filters.get("max_quality"):
            where_conditions.append("quality_score <= ?")
            params.append(filters["max_quality"])
            
        if filters.get("since"):
            where_conditions.append("timestamp >= ?")
            params.append(int(filters["since"]))
            
        # Construct final query
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        cursor.execute(f"""
            SELECT id FROM insights 
            WHERE {where_clause}
            ORDER BY quality_score DESC, timestamp DESC
            LIMIT ?
        """, params + [limit])
        
        insight_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        insights = self._fetch_insights_batch(insight_ids, include_engagement=True)
        
        self._cache_set(cache_key, insights)
        return insights
        
    def get_performance_stats(self) -> Dict:
        """Get comprehensive performance statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get total counts
        cursor.execute("SELECT COUNT(*) FROM insights")
        total_insights = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM agent_performance")
        total_agents = cursor.fetchone()[0]
        
        # Get quality distribution
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN quality_score >= 0.9 THEN 'excellent'
                    WHEN quality_score >= 0.7 THEN 'good'
                    WHEN quality_score >= 0.5 THEN 'fair'
                    ELSE 'poor'
                END as quality_band,
                COUNT(*) as count
            FROM insights 
            GROUP BY quality_band
        """)
        
        quality_dist = dict(cursor.fetchall())
        
        # Get recent activity
        cursor.execute("""
            SELECT COUNT(*) FROM insights 
            WHERE timestamp >= ?
        """, (int(time.time() - 86400),))  # Last 24 hours
        
        recent_insights = cursor.fetchone()[0]
        
        # Get top performing agents
        cursor.execute("""
            SELECT agent_name, total_insights, avg_quality, avg_engagement
            FROM agent_performance 
            ORDER BY avg_quality DESC, total_insights DESC
            LIMIT 10
        """)
        
        top_agents = [
            {
                "agent": row[0],
                "insights": row[1],
                "avg_quality": row[2],
                "avg_engagement": row[3]
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            "total_insights": total_insights,
            "total_agents": total_agents,
            "recent_insights_24h": recent_insights,
            "quality_distribution": quality_dist,
            "top_agents": top_agents,
            "cache_stats": {
                "cached_items": len(self.cache),
                "cache_hit_rate": self._calculate_cache_hit_rate()
            },
            "index_stats": {
                "domains": len(self.indexes["domain"]),
                "categories": len(self.indexes["category"]),
                "agents": len(self.indexes["agent"])
            }
        }
        
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate (simplified)."""
        # This would track actual hits/misses in a real implementation
        return 0.85  # Placeholder
        
    def optimize_database(self):
        """Run database optimization and maintenance."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Analyze tables for better query planning
        cursor.execute("ANALYZE")
        
        # Vacuum to reclaim space
        cursor.execute("VACUUM")
        
        # Update table statistics
        cursor.execute("PRAGMA optimize")
        
        conn.close()
        
        # Rebuild indexes
        self._load_indexes()
        
        logger.info("Database optimization completed")


# Singleton instance
_insight_store = None

def get_insight_store() -> OptimizedInsightStore:
    """Get the optimized insight store singleton."""
    global _insight_store
    
    if _insight_store is None:
        _insight_store = OptimizedInsightStore()
        
    return _insight_store

# Convenience functions
def store_insight(insight_data: Dict) -> str:
    """Store insight with optimization."""
    return get_insight_store().store_insight(insight_data)

def get_insights_by_domain(domain: str, limit: int = 100) -> List[Dict]:
    """Get insights for domain ultra-fast."""
    return get_insight_store().get_insights_by_domain(domain, limit)

def get_recent_insights(hours: int = 24, limit: int = 100) -> List[Dict]:
    """Get recent insights lightning fast."""
    return get_insight_store().get_recent_insights(hours, limit)

def search_insights(query: str, filters: Dict = None, limit: int = 50) -> List[Dict]:
    """Search insights with advanced filtering."""
    return get_insight_store().search_insights(query, filters, limit)

def get_performance_stats() -> Dict:
    """Get comprehensive performance statistics."""
    return get_insight_store().get_performance_stats()

if __name__ == "__main__":
    # Test the optimized store
    store = get_insight_store()
    
    # Test data
    test_insight = {
        "id": "test_001",
        "domain": "example.com",
        "category": "tech",
        "agent_name": "test_agent",
        "type": "comparative_insight",
        "quality_score": 0.92,
        "engagement_score": 0.78,
        "content": "Test insight with high quality"
    }
    
    # Store insight
    insight_id = store.store_insight(test_insight)
    print(f"Stored insight: {insight_id}")
    
    # Retrieve insights
    domain_insights = store.get_insights_by_domain("example.com")
    print(f"Retrieved {len(domain_insights)} insights for example.com")
    
    # Performance stats
    stats = store.get_performance_stats()
    print(f"Performance stats: {stats}")