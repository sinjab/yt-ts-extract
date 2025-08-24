#!/usr/bin/env python3
"""
Updated debug script using Android client approach (no API key needed)
Based on the working 2025 JavaScript method
"""

import requests
import json
import xml.etree.ElementTree as ET
from html import unescape
import re

def test_android_client_approach(video_id: str = "wIwCTQZ_xFE"):
    """Test the Android client approach that doesn't require API key extraction"""
    
    print(f"🤖 Testing Android client approach for video: {video_id}")
    
    session = requests.Session()
    
    # Use Android client headers
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'com.google.android.youtube/20.10.38 (Linux; U; Android 14) gzip',
        'X-YouTube-Client-Name': '3',  # Android client
        'X-YouTube-Client-Version': '20.10.38',
    }
    
    # Try to get API key from YouTube homepage first
    print("🔍 Attempting to extract API key from YouTube homepage...")
    try:
        home_response = session.get("https://www.youtube.com", 
                                  headers={
                                      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                                  },
                                  timeout=30)
        home_html = home_response.text
        
        # Try multiple patterns for API key
        api_key_patterns = [
            r'"INNERTUBE_API_KEY":"([^"]+)"',
            r'"innertubeApiKey":"([^"]+)"',
            r'ytcfg\.set\s*\(\s*\{[^}]*"INNERTUBE_API_KEY"\s*:\s*"([^"]+)"',
        ]
        
        api_key = None
        for pattern in api_key_patterns:
            matches = re.findall(pattern, home_html)
            if matches:
                api_key = matches[0]
                print(f"✅ Found API key from homepage: {api_key[:10]}...")
                break
        
        if not api_key:
            print("❌ Could not extract API key from homepage, trying hardcoded key...")
            # Use a known working key (these sometimes work)
            api_key = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"  # Common YouTube API key
            
    except Exception as e:
        print(f"⚠️  Error getting homepage: {e}")
        # Fallback to common API key
        api_key = "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
    
    # Test with extracted or fallback API key
    url = f"https://www.youtube.com/youtubei/v1/player?key={api_key}"
    
    # Android client payload
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
    
    print(f"🤖 Making request to: {url[:50]}...")
    try:
        response = session.post(url, json=payload, headers=headers, timeout=30)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Got successful response from Android client!")
            
            # Check playability
            playability = data.get("playabilityStatus", {})
            status = playability.get("status", "unknown")
            print(f"Video status: {status}")
            
            if status == "OK":
                # Look for captions
                captions = data.get("captions", {}).get("playerCaptionsTracklistRenderer", {})
                tracks = captions.get("captionTracks", [])
                
                if tracks:
                    print(f"🎉 SUCCESS! Found {len(tracks)} caption tracks:")
                    for i, track in enumerate(tracks):
                        lang = track.get('languageCode', 'unknown')
                        name = track.get('name', {}).get('simpleText', 'Unknown')
                        track_type = 'auto-generated' if track.get('kind') == 'asr' else 'manual'
                        print(f"  {i+1}. {name} ({lang}) - {track_type}")
                        print(f"     URL: {track.get('baseUrl', '')[:60]}...")
                    
                    # Test downloading first track
                    if tracks:
                        test_caption_download(tracks[0], session)
                    
                    return True
                else:
                    print("❌ No caption tracks found")
                    return False
            else:
                reason = playability.get("reason", "No reason provided")
                print(f"❌ Video not playable. Status: {status}, Reason: {reason}")
                return False
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text[:300]}...")
            return False
            
    except Exception as e:
        print(f"❌ Error making request: {e}")
        return False

def test_caption_download(track, session):
    """Test downloading and parsing a caption track"""
    print(f"\n📥 Testing caption download...")
    
    base_url = track.get('baseUrl', '')
    if not base_url:
        print("❌ No baseUrl in track")
        return
    
    # Remove format parameter to get XML
    url = re.sub(r'&fmt=\w+', '', base_url)
    print(f"Fetching: {url[:80]}...")
    
    try:
        response = session.get(url, timeout=30)
        if response.status_code == 200:
            xml_content = response.text
            print(f"✅ Downloaded XML ({len(xml_content)} chars)")
            
            # Parse XML
            try:
                root = ET.fromstring(xml_content)
                text_elements = root.findall('.//text')
                
                if text_elements:
                    print(f"✅ Found {len(text_elements)} text segments")
                    print("First 3 segments:")
                    
                    for i, elem in enumerate(text_elements[:3]):
                        start = elem.get('start', '0')
                        duration = elem.get('dur', '0')
                        text = elem.text or ''
                        text = unescape(text).strip()
                        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
                        
                        print(f"  {i+1}. [{start}s] {text[:60]}...")
                        
                    print("🎉 SUCCESS! Caption extraction working!")
                    return True
                else:
                    print("❌ No text elements found in XML")
                    return False
                    
            except ET.ParseError as e:
                print(f"❌ XML parse error: {e}")
                print(f"XML preview: {xml_content[:200]}...")
                return False
        else:
            print(f"❌ Caption download failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Caption download error: {e}")
        return False

def test_alternative_api_keys():
    """Test with known working API keys"""
    print("\n🔑 Testing alternative API keys...")
    
    # Common YouTube API keys that are sometimes used
    test_keys = [
        "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8",
        "AIzaSyA8eiZmM1FaDVjRy-df2KTyQ_vz_yYM39w", 
        "AIzaSyCjc_pVEDi4qsv5MtC2dMXzpIaDoRFLsxw",
        "AIzaSyCtkvNIR1HCEwzsqK6JuE6KqpyjusIRI30",
    ]
    
    video_id = "wIwCTQZ_xFE"
    
    for i, key in enumerate(test_keys, 1):
        print(f"\n🧪 Testing key {i}: {key[:20]}...")
        
        session = requests.Session()
        url = f"https://www.youtube.com/youtubei/v1/player?key={key}"
        
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
            response = session.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                captions = data.get("captions", {}).get("playerCaptionsTracklistRenderer", {})
                tracks = captions.get("captionTracks", [])
                
                if tracks:
                    print(f"  ✅ SUCCESS with key {i}! Found {len(tracks)} tracks")
                    return key
                else:
                    playability = data.get("playabilityStatus", {}).get("status", "unknown")
                    print(f"  ⚠️  Key works but no captions. Status: {playability}")
            else:
                print(f"  ❌ Failed: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("❌ No working API keys found")
    return None

if __name__ == "__main__":
    print("🤖 YouTube Android Client Test")
    print("=" * 50)
    
    # First try the Android client approach
    video_id = "wIwCTQZ_xFE"  # The failing video
    success = test_android_client_approach(video_id)
    
    if not success:
        print("\n" + "=" * 50)
        print("🔄 Trying with alternative API keys...")
        working_key = test_alternative_api_keys()
        
        if working_key:
            print(f"\n✅ Found working API key: {working_key}")
        else:
            print("\n❌ No working methods found")
            print("\n💡 Suggestions:")
            print("  1. YouTube may have blocked this specific video")
            print("  2. Try with a different video ID")
            print("  3. Consider using the official youtube-transcript-api library")
            print("  4. Check if YouTube has updated their API again")
