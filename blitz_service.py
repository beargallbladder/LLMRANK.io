#!/usr/bin/env python3
"""
Persistent Blitz Service
Runs continuous insight generation in the background
"""

from continuous_blitz_engine import start_continuous_blitz, get_blitz_status
import time
import sys

def main():
    print("🚀 STARTING PERSISTENT BLITZ SERVICE")
    print("=" * 50)
    
    # Start the continuous blitz
    result = start_continuous_blitz(target_per_hour=500)
    print(f"✅ Status: {result['status']}")
    print(f"🎯 Target: {result['target_per_hour']}/hour")
    print(f"🔒 Quality Threshold: {result['quality_threshold']}")
    print("💪 Running continuously with brutal quality enforcement...")
    print()
    
    # Keep running and report status
    try:
        minute_counter = 0
        while True:
            time.sleep(60)  # Wait 1 minute
            minute_counter += 1
            
            # Get status every 5 minutes
            if minute_counter % 5 == 0:
                status = get_blitz_status()
                print(f"🔥 [{minute_counter}min] Blitz Status: {status['status']} | "
                      f"Processed: {status['domains_processed']} | "
                      f"Insights: {status['insights_generated']} | "
                      f"Success: {status['success_rate']:.1%}")
            else:
                print(f"⚡ [{minute_counter}min] Blitz engine running...")
                
    except KeyboardInterrupt:
        print("\n🛑 Blitz service stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error in blitz service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()