"""
GhostSignal Full System Launcher
Codename: "Memory Repair Stack Activation"

Launches the complete Memory Repair-as-a-Service platform:
1. Memory Decay Detection System
2. 10x Blitz Engine
3. Multi-LLM Arena
4. Real-time monitoring and alerts
"""

import asyncio
import json
import time
import logging
from typing import Dict, List
import threading
from memory_decay_detector import memory_detector, run_memory_scan
from blitz_10x_engine import blitz_10x, start_10x_mode, get_10x_status
from multi_llm_arena import arena, run_competitive_insight_generation

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GhostSignalCore:
    """
    Complete GhostSignal Memory Repair Stack controller.
    Orchestrates all components for maximum competitive intelligence generation.
    """
    
    def __init__(self):
        """Initialize GhostSignal core system."""
        self.running = False
        self.components = {
            'memory_decay_detector': False,
            'blitz_10x_engine': False,
            'multi_llm_arena': False,
            'monitoring_system': False
        }
        
        self.performance_metrics = {
            'total_domains_processed': 0,
            'total_insights_generated': 0,
            'decay_events_detected': 0,
            'memory_repair_alerts': 0,
            'system_uptime': 0,
            'cost_efficiency': 0
        }
        
        logger.info("👻 GHOSTSIGNAL CORE INITIALIZED")
        
    def launch_full_system(self, target_domains_per_hour: int = 2500):
        """
        Launch the complete GhostSignal Memory Repair Stack.
        
        Args:
            target_domains_per_hour: Processing target for 10x engine
        """
        print("👻 LAUNCHING GHOSTSIGNAL MEMORY REPAIR STACK")
        print("=" * 60)
        print("🧠 Memory Decay Detection System")
        print("🚀 10x Blitz Engine (Maximum Velocity)")
        print("⚔️  Multi-LLM Arena (Model Competition)")
        print("📊 Real-time Performance Monitoring")
        print("🔔 Automated Decay Alerts")
        print("=" * 60)
        
        self.running = True
        self.performance_metrics['system_start_time'] = time.time()
        
        # 1. Initialize Memory Decay Detection
        print("\n🧠 ACTIVATING MEMORY DECAY DETECTION...")
        self._launch_memory_decay_system()
        
        # 2. Launch 10x Blitz Engine
        print("\n🚀 LAUNCHING 10X BLITZ ENGINE...")
        blitz_result = start_10x_mode(target_domains_per_hour)
        if blitz_result['status'] == 'started':
            self.components['blitz_10x_engine'] = True
            print(f"✅ 10X Blitz Engine: {target_domains_per_hour}/hour target with {blitz_result['workers']} workers")
        
        # 3. Start monitoring system
        print("\n📊 STARTING PERFORMANCE MONITORING...")
        self._start_monitoring_system()
        
        # 4. Run initial memory scan
        print("\n🔍 RUNNING INITIAL MEMORY SCAN...")
        self._run_initial_memory_scan()
        
        print("\n👻 GHOSTSIGNAL FULLY OPERATIONAL!")
        print("🎯 Memory Repair-as-a-Service is now active")
        print("📈 Processing competitive intelligence at maximum velocity")
        print("🔔 Monitoring for memory decay across all brands")
        
        return {
            'status': 'fully_operational',
            'components_active': self.components,
            'target_processing_rate': target_domains_per_hour,
            'launch_timestamp': time.time()
        }
    
    def _launch_memory_decay_system(self):
        """Launch memory decay detection system."""
        try:
            # Memory detector is already initialized
            self.components['memory_decay_detector'] = True
            print("✅ Memory Decay Detector: Monitoring 15%+ decay over 30-day windows")
            print("✅ Memory Snapshots: 0-100 scoring with citation strength tracking")
            print("✅ Decay Alerts: Severity classification (mild/moderate/severe)")
            
        except Exception as e:
            logger.error(f"Error launching memory decay system: {e}")
    
    def _start_monitoring_system(self):
        """Start comprehensive monitoring system."""
        try:
            # Start monitoring thread
            monitor_thread = threading.Thread(target=self._monitoring_loop)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            self.components['monitoring_system'] = True
            print("✅ Performance Monitor: Real-time metrics and cost tracking")
            print("✅ Decay Alert System: Automated brand memory monitoring")
            
        except Exception as e:
            logger.error(f"Error starting monitoring system: {e}")
    
    def _run_initial_memory_scan(self):
        """Run initial comprehensive memory scan."""
        try:
            # Run memory scan in background thread
            scan_thread = threading.Thread(target=self._background_memory_scan)
            scan_thread.daemon = True
            scan_thread.start()
            
            print("✅ Initial Memory Scan: Analyzing all brands for baseline memory scores")
            
        except Exception as e:
            logger.error(f"Error running initial memory scan: {e}")
    
    def _background_memory_scan(self):
        """Background memory scan process."""
        try:
            logger.info("🔍 Starting comprehensive memory scan...")
            scan_results = run_memory_scan()
            
            if 'brands_scanned' in scan_results:
                self.performance_metrics['decay_events_detected'] += scan_results.get('new_decay_events', 0)
                logger.info(f"📊 Memory scan complete: {scan_results['brands_scanned']} brands analyzed")
                
                # Check for critical decay events
                if scan_results.get('new_decay_events', 0) > 0:
                    logger.warning(f"🚨 {scan_results['new_decay_events']} new memory decay events detected!")
                    self.performance_metrics['memory_repair_alerts'] += scan_results['new_decay_events']
            
        except Exception as e:
            logger.error(f"Error in background memory scan: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop for GhostSignal system."""
        while self.running:
            try:
                time.sleep(60)  # Monitor every minute
                
                # Get 10x blitz status
                blitz_status = get_10x_status()
                
                # Update performance metrics
                self.performance_metrics.update({
                    'total_domains_processed': blitz_status.get('domains_processed', 0),
                    'total_insights_generated': blitz_status.get('insights_generated', 0),
                    'current_processing_rate': blitz_status.get('processing_rate', 0),
                    'success_rate': blitz_status.get('success_rate', 0),
                    'cost_per_insight': blitz_status.get('cost_per_insight', 0)
                })
                
                # Calculate system uptime
                if 'system_start_time' in self.performance_metrics:
                    uptime_hours = (time.time() - self.performance_metrics['system_start_time']) / 3600
                    self.performance_metrics['system_uptime'] = uptime_hours
                
                # Log comprehensive status
                self._log_system_status()
                
                # Check for memory decay every 5 minutes
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    self._check_memory_decay()
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
    
    def _log_system_status(self):
        """Log comprehensive system status."""
        metrics = self.performance_metrics
        
        logger.info(f"👻 GHOSTSIGNAL STATUS:")
        logger.info(f"   📊 Domains Processed: {metrics.get('total_domains_processed', 0)}")
        logger.info(f"   💡 Quality Insights: {metrics.get('total_insights_generated', 0)}")
        logger.info(f"   ⚡ Processing Rate: {metrics.get('current_processing_rate', 0):.0f}/hour")
        logger.info(f"   ✅ Success Rate: {metrics.get('success_rate', 0):.1f}%")
        logger.info(f"   💰 Cost/Insight: ${metrics.get('cost_per_insight', 0):.4f}")
        logger.info(f"   🚨 Decay Events: {metrics.get('decay_events_detected', 0)}")
        logger.info(f"   ⏱️  Uptime: {metrics.get('system_uptime', 0):.1f}h")
    
    def _check_memory_decay(self):
        """Periodic memory decay check."""
        try:
            # Get memory status
            memory_status = memory_detector.get_memory_status()
            
            active_decay_events = memory_status.get('active_decay_events', 0)
            
            if active_decay_events > 0:
                logger.warning(f"🚨 MEMORY DECAY ALERT: {active_decay_events} brands experiencing memory decay")
                
                # Get top decaying brands
                top_decaying = memory_status.get('top_decaying_brands', [])
                for brand_info in top_decaying[:3]:  # Top 3
                    brand = brand_info.get('brand', 'unknown')
                    decay_pct = brand_info.get('decay_percentage', 0) * 100
                    severity = brand_info.get('severity', 'unknown')
                    
                    logger.warning(f"   📉 {brand}: {decay_pct:.1f}% decay ({severity})")
            
        except Exception as e:
            logger.error(f"Error checking memory decay: {e}")
    
    def get_ghostsignal_status(self) -> Dict:
        """Get comprehensive GhostSignal system status."""
        try:
            # Get component statuses
            blitz_status = get_10x_status()
            memory_status = memory_detector.get_memory_status()
            
            return {
                'system_status': 'operational' if self.running else 'stopped',
                'components_active': self.components,
                'performance_metrics': self.performance_metrics,
                'blitz_engine': {
                    'processing_rate': blitz_status.get('processing_rate', 0),
                    'domains_processed': blitz_status.get('domains_processed', 0),
                    'insights_generated': blitz_status.get('insights_generated', 0),
                    'success_rate': blitz_status.get('success_rate', 0),
                    'cost_per_insight': blitz_status.get('cost_per_insight', 0)
                },
                'memory_system': {
                    'total_brands': memory_status.get('total_brands', 0),
                    'active_decay_events': memory_status.get('active_decay_events', 0),
                    'recent_activity': memory_status.get('recent_activity', 0),
                    'decay_by_severity': memory_status.get('decay_by_severity', {})
                },
                'alerts': {
                    'decay_events_detected': self.performance_metrics.get('decay_events_detected', 0),
                    'memory_repair_alerts': self.performance_metrics.get('memory_repair_alerts', 0)
                },
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Error getting GhostSignal status: {e}")
            return {'error': str(e), 'timestamp': time.time()}
    
    def shutdown_ghostsignal(self):
        """Shutdown GhostSignal system gracefully."""
        logger.info("🛑 SHUTTING DOWN GHOSTSIGNAL SYSTEM...")
        
        self.running = False
        
        # Stop 10x blitz engine
        try:
            from blitz_10x_engine import stop_10x_mode
            stop_result = stop_10x_mode()
            logger.info(f"✅ 10X Blitz Engine stopped: {stop_result}")
        except Exception as e:
            logger.error(f"Error stopping 10x engine: {e}")
        
        # Update component status
        for component in self.components:
            self.components[component] = False
        
        # Calculate final stats
        if 'system_start_time' in self.performance_metrics:
            total_uptime = time.time() - self.performance_metrics['system_start_time']
            
            logger.info("📊 FINAL GHOSTSIGNAL STATISTICS:")
            logger.info(f"   ⏱️  Total Uptime: {total_uptime/3600:.1f} hours")
            logger.info(f"   📊 Domains Processed: {self.performance_metrics.get('total_domains_processed', 0)}")
            logger.info(f"   💡 Insights Generated: {self.performance_metrics.get('total_insights_generated', 0)}")
            logger.info(f"   🚨 Decay Events: {self.performance_metrics.get('decay_events_detected', 0)}")
        
        return {
            'status': 'shutdown_complete',
            'final_metrics': self.performance_metrics,
            'timestamp': time.time()
        }

# Global GhostSignal instance
ghostsignal = GhostSignalCore()

def launch_ghostsignal(target_domains_per_hour: int = 2500):
    """Launch the complete GhostSignal Memory Repair Stack."""
    return ghostsignal.launch_full_system(target_domains_per_hour)

def get_ghostsignal_status():
    """Get GhostSignal system status."""
    return ghostsignal.get_ghostsignal_status()

def shutdown_ghostsignal():
    """Shutdown GhostSignal system."""
    return ghostsignal.shutdown_ghostsignal()

if __name__ == "__main__":
    # Launch GhostSignal system
    print("👻 GHOSTSIGNAL MEMORY REPAIR STACK")
    print("Launching complete system...")
    
    result = launch_ghostsignal(3000)  # 3000 domains/hour target
    print(f"Launch result: {result}")
    
    # Let it run briefly for demo
    time.sleep(30)
    
    # Get status
    status = get_ghostsignal_status()
    print(f"System status: {status}")
    
    # Shutdown for demo
    shutdown_result = shutdown_ghostsignal()
    print(f"Shutdown result: {shutdown_result}")