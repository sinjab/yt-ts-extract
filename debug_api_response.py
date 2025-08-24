#!/usr/bin/env python3
"""Debug script to check API response"""

import requests
import json

# Test the Android client approach
def test_android_client():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    # Get API key from homepage
    print("Getting API key from homepage...")
    response = session.get("https://www.youtube.com")
    html = response.text
    
    import re
    patterns = [
        r'"INNERTUBE_API_KEY":"([^"]+)"',
        r'"innertubeApiKey":"([^"]+)"',
    ]
    
    api_key = None
    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            api_key = match.group(1)
            break
    
    if not api_key:
        api_key = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
    
    print(f"Using API key: {api_key[:15]}...")
    
    # Test API call
    video_id = "wIwCTQZ_xFE"
    url = f"https://www.youtube.com/youtubei/v1/player?key={api_key}"
    
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'com.google.android.youtube/20.10.38 (Linux; U; Android 14) gzip',
        'X-YouTube-Client-Name': '3',
        'X-YouTube-Client-Version': '20.10.38',
    }
    
    payload = {
        "context": {
            "client": {
                "clientName": "ANDROID",
                "clientVersion": "20.10.38",
                "androidSdkVersion": "34"
            }
        },
        "videoId": video_id
    }
    
    print("Making API call...")
    response = session.post(url, json=payload, headers=headers, timeout=30)
    
    print(f"Status code: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response length: {len(response.text)}")
    print(f"First 500 chars: {response.text[:500]}")
    
    if response.text.strip():
        try:
            data = response.json()
            print("✅ Successfully parsed JSON")
            print(f"Keys in response: {list(data.keys())}")
            
            # Check for captions
            if 'captions' in data:
                captions = data['captions'].get('playerCaptionsTracklistRenderer', {})
                tracks = captions.get('captionTracks', [])
                print(f"Found {len(tracks)} caption tracks")
            else:
                print("No captions field found")
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
    else:
        print("❌ Empty response")

if __name__ == "__main__":
    test_android_client()
