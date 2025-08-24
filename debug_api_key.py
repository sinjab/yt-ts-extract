#!/usr/bin/env python3
"""
Debug script to examine YouTube HTML and identify current API key patterns
"""

import requests
import re
import json
from typing import Optional

def debug_api_key_extraction(video_id: str = "wIwCTQZ_xFE"):
    """Debug API key extraction from YouTube HTML"""
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'sec-ch-ua': '"Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
    })
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"🔍 Fetching HTML from: {url}")
    
    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
        html = response.text
        print(f"✅ HTML fetched successfully ({len(html):,} characters)")
        
        # Save HTML for inspection
        html_file = f"debug_{video_id}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"💾 HTML saved to {html_file}")
        
        # Test current patterns
        print("\n🔍 Testing current patterns...")
        current_patterns = [
            r'"INNERTUBE_API_KEY":\s*"([a-zA-Z0-9_-]+)"',
            r'"innertubeApiKey":\s*"([a-zA-Z0-9_-]+)"'
        ]
        
        for i, pattern in enumerate(current_patterns, 1):
            matches = re.findall(pattern, html)
            print(f"  Pattern {i}: {pattern}")
            print(f"    Matches: {matches if matches else 'None'}")
        
        # Look for any API key related patterns
        print("\n🔍 Looking for API key variations...")
        api_patterns = [
            r'"INNERTUBE_API_KEY":"([^"]+)"',
            r'"innertubeApiKey":"([^"]+)"',
            r'"apiKey":"([^"]+)"',
            r'INNERTUBE_API_KEY["\s]*:["\s]*"([^"]+)"',
            r'"key":"([^"]+)".*innertube',
            r'ytInitialData.*?"apiKey":"([^"]+)"',
            r'"INNERTUBE_API_KEY":\s*"([^"]+)"',
            r'ytcfg\.set\s*\(\s*\{[^}]*"INNERTUBE_API_KEY"\s*:\s*"([^"]+)"',
            r'window\["ytInitialData"\][^}]*"INNERTUBE_API_KEY"\s*:\s*"([^"]+)"',
        ]
        
        found_any = False
        for i, pattern in enumerate(api_patterns, 1):
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                found_any = True
                print(f"  ✅ Pattern {i} FOUND: {matches[0][:20]}...")
                return matches[0]  # Return first found key
            else:
                print(f"  ❌ Pattern {i}: No matches")
        
        if not found_any:
            print("\n🔍 Searching for any mention of 'API_KEY' or 'apiKey'...")
            general_search = re.findall(r'["\s](.*API[_-]?KEY.*?)["\s]*:["\s]*([^",\s}]+)', html, re.IGNORECASE)
            if general_search:
                print(f"  Found general API key references: {general_search[:5]}")
            else:
                print("  No API key references found")
            
            # Look for ytcfg or ytInitialData structures
            print("\n🔍 Looking for ytcfg or ytInitialData structures...")
            config_patterns = [
                r'ytcfg\.set\s*\(\s*({.*?})\s*\)',
                r'window\["ytInitialData"\]\s*=\s*({.*?});',
                r'var ytInitialData\s*=\s*({.*?});',
            ]
            
            for pattern in config_patterns:
                matches = re.findall(pattern, html, re.DOTALL)
                for match in matches[:3]:  # Only check first 3 matches
                    if 'API_KEY' in match or 'apiKey' in match:
                        print(f"  Found config with API key: {match[:100]}...")
                        # Try to extract JSON
                        try:
                            # Fix common JSON issues
                            json_str = match.replace("'", '"').replace('undefined', 'null')
                            # Remove trailing commas
                            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
                            config = json.loads(json_str)
                            
                            # Search for API keys in the config
                            api_key = find_api_key_in_dict(config)
                            if api_key:
                                print(f"  ✅ Found API key in config: {api_key[:20]}...")
                                return api_key
                        except json.JSONDecodeError:
                            print(f"  ⚠️  Found config but couldn't parse JSON")
        
        print("\n❌ No API key found with any pattern")
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def find_api_key_in_dict(data, path=""):
    """Recursively search for API keys in nested dictionaries"""
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if any(api_term in key.upper() for api_term in ['API_KEY', 'APIKEY']) and isinstance(value, str):
                print(f"    Found at {current_path}: {value[:20]}...")
                return value
            elif isinstance(value, (dict, list)):
                result = find_api_key_in_dict(value, current_path)
                if result:
                    return result
    elif isinstance(data, list):
        for i, item in enumerate(data):
            current_path = f"{path}[{i}]" if path else f"[{i}]"
            result = find_api_key_in_dict(item, current_path)
            if result:
                return result
    return None

def test_api_key_with_innertube(api_key: str, video_id: str = "wIwCTQZ_xFE"):
    """Test if extracted API key works with Innertube API"""
    if not api_key:
        print("❌ No API key to test")
        return False
    
    print(f"\n🧪 Testing API key with Innertube: {api_key[:10]}...")
    
    session = requests.Session()
    url = f"https://www.youtube.com/youtubei/v1/player?key={api_key}"
    
    # Test with ANDROID client (more reliable according to research)
    payload = {
        "context": {
            "client": {
                "clientName": "ANDROID",
                "clientVersion": "20.10.38"
            }
        },
        "videoId": video_id
    }
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'com.google.android.youtube/20.10.38 (Linux; U; Android 14) gzip',
    }
    
    try:
        response = session.post(url, json=payload, headers=headers, timeout=30)
        print(f"  Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if we got captions
            captions = data.get("captions", {}).get("playerCaptionsTracklistRenderer", {})
            tracks = captions.get("captionTracks", [])
            
            if tracks:
                print(f"  ✅ SUCCESS! Found {len(tracks)} caption tracks")
                for track in tracks[:3]:
                    lang = track.get('languageCode', 'unknown')
                    name = track.get('name', {}).get('simpleText', 'Unknown')
                    print(f"    - {name} ({lang})")
                return True
            else:
                playability = data.get("playabilityStatus", {})
                status = playability.get("status", "unknown")
                reason = playability.get("reason", "No reason provided")
                print(f"  ⚠️  API worked but no captions. Status: {status}, Reason: {reason}")
                return False
        else:
            print(f"  ❌ API request failed: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error testing API: {e}")
        return False

if __name__ == "__main__":
    print("🔍 YouTube API Key Debug Tool")
    print("=" * 50)
    
    # Test with the failing video
    video_id = "wIwCTQZ_xFE"
    api_key = debug_api_key_extraction(video_id)
    
    if api_key:
        success = test_api_key_with_innertube(api_key, video_id)
        if success:
            print(f"\n✅ SUCCESS: API key works! Key: {api_key}")
        else:
            print(f"\n⚠️  API key found but doesn't work for captions: {api_key}")
    else:
        print("\n❌ Could not extract API key from HTML")
        print("\n💡 Next steps:")
        print("  1. Check the saved HTML file for manual inspection")
        print("  2. Try with a different video ID")
        print("  3. Check if YouTube has changed their HTML structure")
