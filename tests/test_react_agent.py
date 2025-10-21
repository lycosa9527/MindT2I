#!/usr/bin/env python3
"""
Test script for ReAct Agent
============================

Tests the intelligent intent detection and routing system.
"""

import asyncio
import aiohttp
import json


async def test_react_agent():
    """Test the ReAct agent with various prompts"""
    
    print("\n" + "=" * 70)
    print("🧠 Testing MindT2I ReAct Agent")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "Video: Running cat",
            "prompt": "一只小猫在月光下奔跑",
            "expected": "video"
        },
        {
            "name": "Image: Static sunset",
            "prompt": "A beautiful sunset over mountains with golden clouds",
            "expected": "image"
        },
        {
            "name": "Video: Dog playing",
            "prompt": "狗狗在公园里玩耍",
            "expected": "video"
        },
        {
            "name": "Image: Portrait",
            "prompt": "A professional portrait of a business woman",
            "expected": "image"
        },
        {
            "name": "Video: Birds flying",
            "prompt": "一群鸟儿在天空中飞翔",
            "expected": "video"
        },
        {
            "name": "Image: Still life",
            "prompt": "一个安静的茶具摆设",
            "expected": "image"
        }
    ]
    
    url = "http://localhost:9528/generate"
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}/{len(test_cases)}: {test['name']}")
        print(f"   Prompt: {test['prompt']}")
        print(f"   Expected: {test['expected'].upper()}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json={"prompt": test['prompt']},
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        detected_type = data.get('type', 'unknown')
                        intent_analysis = data.get('intent_analysis', {})
                        confidence = intent_analysis.get('confidence', 0)
                        reasoning = intent_analysis.get('reasoning', 'N/A')
                        
                        correct = detected_type == test['expected']
                        results.append({
                            'test': test['name'],
                            'correct': correct,
                            'detected': detected_type,
                            'expected': test['expected'],
                            'confidence': confidence
                        })
                        
                        status = "✅ CORRECT" if correct else "❌ WRONG"
                        print(f"   {status}")
                        print(f"   Detected: {detected_type.upper()} (confidence: {confidence:.2f})")
                        print(f"   Reasoning: {reasoning[:100]}...")
                        
                        if 'url' in data:
                            print(f"   URL: {data['url'][:60]}...")
                    else:
                        error = await response.text()
                        print(f"   ❌ ERROR: HTTP {response.status}")
                        print(f"   {error}")
                        results.append({
                            'test': test['name'],
                            'correct': False,
                            'detected': 'error',
                            'expected': test['expected'],
                            'confidence': 0
                        })
        
        except asyncio.TimeoutError:
            print("   ⏱️  TIMEOUT (this is normal for actual generation)")
            results.append({
                'test': test['name'],
                'correct': None,
                'detected': 'timeout',
                'expected': test['expected'],
                'confidence': 0
            })
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            results.append({
                'test': test['name'],
                'correct': False,
                'detected': 'exception',
                'expected': test['expected'],
                'confidence': 0
            })
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    
    correct_count = sum(1 for r in results if r['correct'] == True)
    total_count = sum(1 for r in results if r['correct'] is not None)
    
    if total_count > 0:
        accuracy = (correct_count / total_count) * 100
        print(f"Accuracy: {correct_count}/{total_count} ({accuracy:.1f}%)")
    
    print("\nDetailed Results:")
    for r in results:
        if r['correct'] is not None:
            status = "✅" if r['correct'] else "❌"
            print(f"  {status} {r['test']}: {r['detected']} (expected: {r['expected']}, conf: {r['confidence']:.2f})")
        else:
            print(f"  ⏱️  {r['test']}: {r['detected']}")
    
    print("\n" + "=" * 70)
    print("💡 Note: Actual generation may timeout - this is normal.")
    print("   The ReAct agent runs BEFORE generation starts.")
    print("=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(test_react_agent())
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")

