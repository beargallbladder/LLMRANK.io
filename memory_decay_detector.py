"""
Memory Decay Detection System
Codename: "GhostSignal-Core"

Implements the memory decay detection engine from PRD-46.
Tracks brand memory scores across LLMs and triggers alerts when
memory decay is detected (>15% drop over 30 days).
"""

import json
import time
import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MemorySnapshot:
    """Represents a memory measurement at a specific time."""
    brand: str
    model: str
    memory_score: float  # 0-100
    confidence: float
    timestamp: float
    insight_count: int
    citation_strength: float
    semantic_similarity: float

@dataclass
class DecayEvent:
    """Represents a detected memory decay event."""
    brand: str
    model: str
    severity: str  # 'mild', 'moderate', 'severe'
    decay_percentage: float
    time_period_days: int
    triggered_at: float
    current_score: float
    previous_score: float
    status: str = 'active'  # 'active', 'resolved', 'ignored'

class MemoryDecayDetector:
    """
    Core memory decay detection system that monitors brand memory
    across LLMs and triggers alerts when significant decay is detected.
    """
    
    def __init__(self):
        """Initialize the memory decay detector."""
        self.memory_history_file = 'data/memory_snapshots.json'
        self.decay_events_file = 'data/decay_events.json'
        self.memory_snapshots = []
        self.decay_events = []
        self.decay_threshold = 0.15  # 15% decay threshold
        self.monitoring_window_days = 30
        
        # Load existing data
        self.load_memory_data()
        
        logger.info("🧠 MEMORY DECAY DETECTOR INITIALIZED")
        logger.info(f"📊 Loaded {len(self.memory_snapshots)} memory snapshots")
        logger.info(f"🚨 {len([e for e in self.decay_events if e.status == 'active'])} active decay events")

    def load_memory_data(self):
        """Load existing memory snapshots and decay events."""
        try:
            # Load memory snapshots
            if os.path.exists(self.memory_history_file):
                with open(self.memory_history_file, 'r') as f:
                    snapshot_data = json.load(f)
                    self.memory_snapshots = [
                        MemorySnapshot(**data) for data in snapshot_data
                    ]
            
            # Load decay events
            if os.path.exists(self.decay_events_file):
                with open(self.decay_events_file, 'r') as f:
                    event_data = json.load(f)
                    self.decay_events = [
                        DecayEvent(**data) for data in event_data
                    ]
                    
        except Exception as e:
            logger.error(f"Error loading memory data: {e}")
            self.memory_snapshots = []
            self.decay_events = []

    def save_memory_data(self):
        """Save memory snapshots and decay events to files."""
        try:
            os.makedirs('data', exist_ok=True)
            
            # Save memory snapshots
            snapshot_data = [
                {
                    'brand': s.brand,
                    'model': s.model,
                    'memory_score': s.memory_score,
                    'confidence': s.confidence,
                    'timestamp': s.timestamp,
                    'insight_count': s.insight_count,
                    'citation_strength': s.citation_strength,
                    'semantic_similarity': s.semantic_similarity
                }
                for s in self.memory_snapshots
            ]
            
            with open(self.memory_history_file, 'w') as f:
                json.dump(snapshot_data, f, indent=2)
            
            # Save decay events
            event_data = [
                {
                    'brand': e.brand,
                    'model': e.model,
                    'severity': e.severity,
                    'decay_percentage': e.decay_percentage,
                    'time_period_days': e.time_period_days,
                    'triggered_at': e.triggered_at,
                    'current_score': e.current_score,
                    'previous_score': e.previous_score,
                    'status': e.status
                }
                for e in self.decay_events
            ]
            
            with open(self.decay_events_file, 'w') as f:
                json.dump(event_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving memory data: {e}")

    def calculate_memory_score(self, brand: str, model: str, insights: List[Dict]) -> MemorySnapshot:
        """
        Calculate comprehensive memory score for a brand/model combination.
        
        Args:
            brand: Brand domain (e.g., 'stripe.com')
            model: Model identifier (e.g., 'gpt-4o', 'claude-3')
            insights: List of insights for this brand/model
            
        Returns:
            MemorySnapshot with calculated scores
        """
        if not insights:
            return MemorySnapshot(
                brand=brand,
                model=model,
                memory_score=0.0,
                confidence=0.0,
                timestamp=time.time(),
                insight_count=0,
                citation_strength=0.0,
                semantic_similarity=0.0
            )
        
        # Filter recent insights (last 30 days)
        current_time = time.time()
        recent_insights = [
            insight for insight in insights 
            if current_time - insight.get('timestamp', 0) < (30 * 24 * 3600)
        ]
        
        if not recent_insights:
            recent_insights = insights[-5:]  # Fallback to latest 5
        
        # Calculate component scores
        insight_count = len(recent_insights)
        
        # Quality score average (weighted by recency)
        quality_scores = []
        for insight in recent_insights:
            quality = insight.get('quality_score', 0)
            age_days = (current_time - insight.get('timestamp', 0)) / 86400
            weight = max(0.1, 1.0 - (age_days / 30))  # Decay weight over 30 days
            quality_scores.append(quality * weight)
        
        avg_quality = np.mean(quality_scores) if quality_scores else 0
        
        # Citation strength (based on content richness and specificity)
        citation_scores = []
        for insight in recent_insights:
            content = insight.get('content', '')
            # Score based on specific brand mentions, competitive terms, etc.
            brand_clean = brand.replace('.com', '').replace('.', ' ')
            
            citation_score = 0
            if brand_clean.lower() in content.lower():
                citation_score += 0.3
            if any(word in content.lower() for word in ['leading', 'dominant', 'innovative']):
                citation_score += 0.2
            if any(word in content.lower() for word in ['competitive', 'advantage', 'market']):
                citation_score += 0.3
            if len(content) > 300:
                citation_score += 0.2
                
            citation_scores.append(min(citation_score, 1.0))
        
        citation_strength = np.mean(citation_scores) if citation_scores else 0
        
        # Semantic similarity (consistency across insights)
        if len(recent_insights) > 1:
            # Simple similarity based on common keywords
            all_words = []
            for insight in recent_insights:
                words = insight.get('content', '').lower().split()
                all_words.extend(words)
            
            # Calculate word frequency consistency
            word_freq = {}
            for word in all_words:
                if len(word) > 4:  # Only meaningful words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Semantic similarity based on consistent terminology
            consistent_terms = sum(1 for count in word_freq.values() if count > 1)
            semantic_similarity = min(consistent_terms / 10, 1.0)  # Normalize to 0-1
        else:
            semantic_similarity = avg_quality  # Single insight uses quality as similarity
        
        # Calculate overall memory score (0-100)
        memory_score = (
            avg_quality * 40 +           # 40% quality weight
            citation_strength * 30 +     # 30% citation weight  
            semantic_similarity * 20 +   # 20% consistency weight
            min(insight_count / 10, 1.0) * 10  # 10% volume weight
        ) * 100
        
        # Confidence based on data availability and quality
        confidence = min(
            (insight_count / 5) * 0.5 +  # 50% from volume
            avg_quality * 0.5,           # 50% from quality
            1.0
        )
        
        return MemorySnapshot(
            brand=brand,
            model=model,
            memory_score=memory_score,
            confidence=confidence,
            timestamp=current_time,
            insight_count=insight_count,
            citation_strength=citation_strength,
            semantic_similarity=semantic_similarity
        )

    def detect_memory_decay(self, brand: str, model: str) -> Optional[DecayEvent]:
        """
        Detect memory decay for a specific brand/model combination.
        
        Args:
            brand: Brand domain
            model: Model identifier
            
        Returns:
            DecayEvent if decay detected, None otherwise
        """
        # Get memory snapshots for this brand/model
        brand_snapshots = [
            snapshot for snapshot in self.memory_snapshots
            if snapshot.brand == brand and snapshot.model == model
        ]
        
        if len(brand_snapshots) < 2:
            return None  # Need at least 2 snapshots to detect decay
        
        # Sort by timestamp
        brand_snapshots.sort(key=lambda x: x.timestamp)
        
        current_snapshot = brand_snapshots[-1]
        current_time = time.time()
        
        # Look for decay over monitoring window
        window_start = current_time - (self.monitoring_window_days * 24 * 3600)
        
        # Find baseline snapshot from beginning of window
        baseline_snapshot = None
        for snapshot in reversed(brand_snapshots[:-1]):
            if snapshot.timestamp >= window_start:
                baseline_snapshot = snapshot
                break
        
        if not baseline_snapshot:
            # Use oldest available snapshot if no snapshot in window
            baseline_snapshot = brand_snapshots[0]
        
        # Calculate decay percentage
        if baseline_snapshot.memory_score == 0:
            return None  # Can't calculate decay from zero baseline
            
        decay_percentage = (baseline_snapshot.memory_score - current_snapshot.memory_score) / baseline_snapshot.memory_score
        
        # Check if decay exceeds threshold
        if decay_percentage >= self.decay_threshold:
            # Determine severity
            if decay_percentage >= 0.3:
                severity = 'severe'
            elif decay_percentage >= 0.2:
                severity = 'moderate'
            else:
                severity = 'mild'
            
            # Check if we already have an active decay event for this brand/model
            existing_event = None
            for event in self.decay_events:
                if (event.brand == brand and event.model == model and 
                    event.status == 'active'):
                    existing_event = event
                    break
            
            if existing_event:
                # Update existing event if decay worsened
                if decay_percentage > existing_event.decay_percentage:
                    existing_event.decay_percentage = decay_percentage
                    existing_event.severity = severity
                    existing_event.current_score = current_snapshot.memory_score
                    return existing_event
                return None
            else:
                # Create new decay event
                time_period = int((current_snapshot.timestamp - baseline_snapshot.timestamp) / 86400)
                
                decay_event = DecayEvent(
                    brand=brand,
                    model=model,
                    severity=severity,
                    decay_percentage=decay_percentage,
                    time_period_days=time_period,
                    triggered_at=current_time,
                    current_score=current_snapshot.memory_score,
                    previous_score=baseline_snapshot.memory_score,
                    status='active'
                )
                
                self.decay_events.append(decay_event)
                
                logger.warning(f"🚨 MEMORY DECAY DETECTED: {brand} ({model}) - "
                             f"{decay_percentage:.1%} decay over {time_period} days")
                
                return decay_event
        
        return None

    def process_brand_insights(self, brand: str) -> Dict:
        """
        Process all insights for a brand and update memory snapshots.
        
        Args:
            brand: Brand domain to process
            
        Returns:
            Dictionary with memory scores and any decay events
        """
        try:
            # Load insights from blitz engine
            with open('data/insights/insight_log.json', 'r') as f:
                all_insights = json.load(f)
            
            # Filter insights for this brand
            brand_insights = [
                insight for insight in all_insights
                if insight.get('domain') == brand
            ]
            
            if not brand_insights:
                return {'brand': brand, 'status': 'no_insights'}
            
            # Group insights by model
            insights_by_model = {}
            for insight in brand_insights:
                model = insight.get('model', 'unknown')
                if model not in insights_by_model:
                    insights_by_model[model] = []
                insights_by_model[model].append(insight)
            
            results = {
                'brand': brand,
                'memory_snapshots': {},
                'decay_events': [],
                'timestamp': time.time()
            }
            
            # Calculate memory scores for each model
            for model, insights in insights_by_model.items():
                # Calculate new memory snapshot
                snapshot = self.calculate_memory_score(brand, model, insights)
                self.memory_snapshots.append(snapshot)
                results['memory_snapshots'][model] = {
                    'memory_score': snapshot.memory_score,
                    'confidence': snapshot.confidence,
                    'insight_count': snapshot.insight_count,
                    'citation_strength': snapshot.citation_strength
                }
                
                # Check for decay
                decay_event = self.detect_memory_decay(brand, model)
                if decay_event:
                    results['decay_events'].append({
                        'model': model,
                        'severity': decay_event.severity,
                        'decay_percentage': decay_event.decay_percentage,
                        'current_score': decay_event.current_score,
                        'previous_score': decay_event.previous_score
                    })
            
            # Save updated data
            self.save_memory_data()
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing brand {brand}: {e}")
            return {'brand': brand, 'status': 'error', 'error': str(e)}

    def get_memory_status(self, brand: Optional[str] = None) -> Dict:
        """
        Get current memory status for all brands or a specific brand.
        
        Args:
            brand: Optional specific brand to check
            
        Returns:
            Memory status summary
        """
        current_time = time.time()
        
        if brand:
            # Get status for specific brand
            brand_snapshots = [s for s in self.memory_snapshots if s.brand == brand]
            brand_events = [e for e in self.decay_events if e.brand == brand and e.status == 'active']
            
            return {
                'brand': brand,
                'snapshots': len(brand_snapshots),
                'active_decay_events': len(brand_events),
                'latest_scores': {
                    snapshot.model: snapshot.memory_score 
                    for snapshot in brand_snapshots[-3:] 
                },
                'decay_events': [
                    {
                        'model': e.model,
                        'severity': e.severity,
                        'decay_percentage': e.decay_percentage
                    } for e in brand_events
                ]
            }
        else:
            # Get overall status
            active_events = [e for e in self.decay_events if e.status == 'active']
            
            # Get unique brands
            brands = set(s.brand for s in self.memory_snapshots)
            
            # Recent activity (last 24 hours)
            recent_snapshots = [
                s for s in self.memory_snapshots 
                if current_time - s.timestamp < 86400
            ]
            
            return {
                'total_brands': len(brands),
                'total_snapshots': len(self.memory_snapshots),
                'active_decay_events': len(active_events),
                'recent_activity': len(recent_snapshots),
                'decay_by_severity': {
                    'severe': len([e for e in active_events if e.severity == 'severe']),
                    'moderate': len([e for e in active_events if e.severity == 'moderate']),
                    'mild': len([e for e in active_events if e.severity == 'mild'])
                },
                'top_decaying_brands': [
                    {
                        'brand': e.brand,
                        'model': e.model,
                        'decay_percentage': e.decay_percentage,
                        'severity': e.severity
                    }
                    for e in sorted(active_events, key=lambda x: x.decay_percentage, reverse=True)[:5]
                ]
            }

    def run_full_memory_scan(self) -> Dict:
        """
        Run memory decay detection across all brands in the system.
        
        Returns:
            Summary of scan results
        """
        logger.info("🧠 Starting full memory decay scan...")
        
        try:
            # Get all unique brands from insights
            with open('data/insights/insight_log.json', 'r') as f:
                all_insights = json.load(f)
            
            brands = set(insight.get('domain') for insight in all_insights if insight.get('domain'))
            
            scan_results = {
                'scan_timestamp': time.time(),
                'brands_scanned': 0,
                'new_decay_events': 0,
                'total_memory_snapshots': 0,
                'brands_processed': []
            }
            
            for brand in brands:
                result = self.process_brand_insights(brand)
                scan_results['brands_scanned'] += 1
                scan_results['new_decay_events'] += len(result.get('decay_events', []))
                scan_results['total_memory_snapshots'] += len(result.get('memory_snapshots', {}))
                scan_results['brands_processed'].append(result)
                
                # Log progress
                if scan_results['brands_scanned'] % 10 == 0:
                    logger.info(f"📊 Processed {scan_results['brands_scanned']}/{len(brands)} brands")
            
            logger.info(f"✅ Memory scan complete: {scan_results['brands_scanned']} brands, "
                       f"{scan_results['new_decay_events']} new decay events detected")
            
            return scan_results
            
        except Exception as e:
            logger.error(f"Error during memory scan: {e}")
            return {'error': str(e), 'scan_timestamp': time.time()}

# Global detector instance
memory_detector = MemoryDecayDetector()

def detect_memory_decay_for_brand(brand: str) -> Dict:
    """Process memory decay detection for a specific brand."""
    return memory_detector.process_brand_insights(brand)

def get_memory_status(brand: Optional[str] = None) -> Dict:
    """Get memory status summary."""
    return memory_detector.get_memory_status(brand)

def run_memory_scan() -> Dict:
    """Run full memory decay scan."""
    return memory_detector.run_full_memory_scan()

if __name__ == "__main__":
    # Test the memory decay detector
    print("🧠 Testing Memory Decay Detector")
    
    # Run scan on current data
    results = run_memory_scan()
    print(f"Scan Results: {results}")
    
    # Get overall status
    status = get_memory_status()
    print(f"Memory Status: {status}")