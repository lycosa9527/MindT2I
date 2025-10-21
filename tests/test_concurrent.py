#!/usr/bin/env python3
"""
Test concurrent video generation
================================

Tests the system's ability to handle multiple simultaneous video requests.
"""

import asyncio
import aiohttp
import time
from datetime import datetime


async def generate_video(session, user_id):
    """Simulate a single user generating a video"""
    start_time = time.time()
    
    print(f"[User {user_id}] Starting request at {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        async with session.post(
            "http://localhost:9528/generate-video",
            json={"prompt": f"Test video for user {user_id}"},
            timeout=aiohttp.ClientTimeout(total=300)
        ) as response:
            if response.status == 200:
                result = await response.text()
                elapsed = time.time() - start_time
                print(f"[User {user_id}] ✅ SUCCESS in {elapsed:.1f}s - {result[:50]}...")
                return {"user": user_id, "success": True, "time": elapsed}
            else:
                error = await response.text()
                elapsed = time.time() - start_time
                print(f"[User {user_id}] ❌ ERROR in {elapsed:.1f}s - {error[:100]}")
                return {"user": user_id, "success": False, "time": elapsed}
                
    except asyncio.TimeoutError:
        elapsed = time.time() - start_time
        print(f"[User {user_id}] ⏱️ TIMEOUT after {elapsed:.1f}s")
        return {"user": user_id, "success": False, "time": elapsed, "timeout": True}
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"[User {user_id}] ❌ EXCEPTION in {elapsed:.1f}s - {e}")
        return {"user": user_id, "success": False, "time": elapsed, "error": str(e)}


async def load_test(num_users=5):
    """Test with multiple concurrent users"""
    
    print("\n" + "=" * 70)
    print(f"🧪 CONCURRENT LOAD TEST: {num_users} Users")
    print("=" * 70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    start_time = time.time()
    
    # Create session for all requests
    async with aiohttp.ClientSession() as session:
        # Launch all requests simultaneously
        tasks = [generate_video(session, i+1) for i in range(num_users)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    
    total_time = time.time() - start_time
    
    # Analyze results
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS")
    print("=" * 70)
    
    successful = sum(1 for r in results if isinstance(r, dict) and r.get('success'))
    failed = num_users - successful
    
    print(f"Total requests: {num_users}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/num_users)*100:.1f}%")
    print(f"Total test time: {total_time:.1f}s")
    
    if successful > 0:
        times = [r['time'] for r in results if isinstance(r, dict) and r.get('success')]
        print(f"\nResponse times:")
        print(f"  Min: {min(times):.1f}s")
        print(f"  Max: {max(times):.1f}s")
        print(f"  Avg: {sum(times)/len(times):.1f}s")
    
    print("\n" + "=" * 70)
    print("💡 Notes:")
    print("  - Videos take 1-5 minutes to generate")
    print("  - System handles up to 20 concurrent generations")
    print("  - Downloads limited to 10 concurrent")
    print("  - This test demonstrates non-blocking async behavior")
    print("=" * 70)


async def quick_test():
    """Quick test with 3 users"""
    await load_test(3)


async def stress_test():
    """Stress test with 10 users"""
    await load_test(10)


async def max_test():
    """Maximum test with 25 users (exceeds semaphore limit)"""
    print("\n⚠️  This will exceed the 20 concurrent generation limit")
    print("Some requests will queue and wait for others to complete\n")
    await load_test(25)


if __name__ == "__main__":
    import sys
    
    print("\n🎬 MindT2I Concurrent Load Test")
    print("Make sure the server is running: python main.py\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == "stress":
        print("Running STRESS TEST (10 users)...")
        asyncio.run(stress_test())
    elif len(sys.argv) > 1 and sys.argv[1] == "max":
        print("Running MAX TEST (25 users)...")
        asyncio.run(max_test())
    else:
        print("Running QUICK TEST (3 users)...")
        print("For more users: python test_concurrent.py stress")
        print("For maximum load: python test_concurrent.py max\n")
        asyncio.run(quick_test())

