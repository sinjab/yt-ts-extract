#!/usr/bin/env python3
"""
Enhanced debug script to analyze YouTube's current API access methods
"""

import requests
import re
import time
from random import uniform
import logging
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class YouTubeAdvancedDebugger:
    """Advanced debug class to find current YouTube API access methods"""
    
    def __init__(self):
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_delay = 2
        
        # Enhanced headers - latest Chrome user agent and all modern headers
        self.session.headers.update({
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
    
    def _wait_if_needed(self):
        """Rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay:
            delay = self.min_delay - elapsed + uniform(0, 1)
            time.sleep(delay)
        self.last_request_time = time.time()
    
    def get_video_html(self, video_id: str) -> str:
        """Fetch YouTube video page HTML with proper encoding"""
        self._wait_if_needed()
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        logger.info(f"Fetching: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Content-Type: {response.headers.get('Content-Type')}")
            logger.info(f"Content-Encoding: {response.headers.get('Content-Encoding')}")
            
            # Check for blocks
            if "blocked" in response.text.lower() or response.status_code == 429:
                raise Exception(f"IP blocked (429) for video {video_id}")
            
            if "recaptcha" in response.text.lower():
                raise Exception(f"IP blocked (reCAPTCHA) for video {video_id}")
            
            response.raise_for_status()
            
            # Make sure we have decoded text
            html_content = response.text
            logger.info(f"Successfully fetched video page ({len(html_content)} chars)")
            return html_content
            
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch video page: {e}")
    
    def try_embedded_player(self, video_id: str):
        """Try the embedded player approach which might have different API access"""
        print(f"\n🎬 Trying embedded player approach for: {video_id}")
        
        # Try embedded URL
        embed_url = f"https://www.youtube.com/embed/{video_id}"
        try:
            self._wait_if_needed()
            response = self.session.get(embed_url, timeout=10)
            
            if response.status_code == 200:
                html = response.text
                print(f"✅ Embedded page fetched ({len(html)} chars)")
                
                # Look for API keys in embedded page
                patterns = [
                    r'"INNERTUBE_API_KEY":\s*"([^"]+)"',
                    r'"innertubeApiKey":\s*"([^"]+)"',
                    r'"apiKey":\s*"([^"]+)"',
                    r'api_key[\'"]?\s*:\s*[\'"]([^\'"]+)[\'"]',
                    r'key[\'"]?\s*:\s*[\'"]([A-Za-z0-9_-]{20,})[\'"]',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, html, re.IGNORECASE)
                    if matches:
                        print(f"✅ Found API key(s) in embedded page: {matches}")
                        return matches[0]
                
                print("❌ No API keys found in embedded page")
                
                # Save for inspection
                with open(f'debug_embed_{video_id}.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"📝 Embedded HTML saved for inspection")
                
            else:
                print(f"❌ Embedded page failed: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Embedded approach failed: {e}")
    
    def try_mobile_approach(self, video_id: str):
        """Try mobile YouTube which might use different API structure"""
        print(f"\n📱 Trying mobile approach for: {video_id}")
        
        # Create mobile session
        mobile_session = requests.Session()
        mobile_session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        mobile_url = f"https://m.youtube.com/watch?v={video_id}"
        try:
            self._wait_if_needed()
            response = mobile_session.get(mobile_url, timeout=10)
            
            if response.status_code == 200:
                html = response.text
                print(f"✅ Mobile page fetched ({len(html)} chars)")
                
                # Save for inspection
                with open(f'debug_mobile_{video_id}.html', 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"📝 Mobile HTML saved for inspection")
                
                # Look for mobile-specific patterns
                mobile_patterns = [
                    r'"c":\s*"WEB"[^}]*"apiKey":\s*"([^"]+)"',
                    r'"client"[^}]*"apiKey":\s*"([^"]+)"',
                    r'ytplayer[^}]*"apiKey":\s*"([^"]+)"',
                    r'"INNERTUBE_API_KEY":\s*"([^"]+)"',
                ]
                
                for pattern in mobile_patterns:
                    matches = re.findall(pattern, html, re.IGNORECASE)
                    if matches:
                        print(f"✅ Found mobile API key(s): {matches}")
                        return matches[0]
                
                print("❌ No API keys found in mobile page")
            else:
                print(f"❌ Mobile page failed: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Mobile approach failed: {e}")
    
    def try_direct_innertube(self):
        """Try to make a direct call to Innertube API without API key to see what happens"""
        print(f"\n🔌 Trying direct Innertube API call without key...")
        
        innertube_url = "https://www.youtube.com/youtubei/v1/player"
        
        # YouTube's typical client context
        context = {
            "client": {
                "clientName": "WEB",
                "clientVersion": "2.20250824.08.00"
            }
        }
        
        payload = {
            "context": context,
            "videoId": "wIwCTQZ_xFE"
        }
        
        try:
            self._wait_if_needed()
            response = self.session.post(innertube_url, json=payload, timeout=10)
            
            print(f"Response status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Direct API call worked! No API key needed?")
                data = response.json()
                
                # Check if we got captions
                if 'captions' in data:
                    print("✅ Captions found in response!")
                    return data
                else:
                    print("❌ No captions in response")
                    print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            else:
                print(f"❌ API call failed: {response.status_code}")
                print(f"Response: {response.text[:500]}...")
        
        except Exception as e:
            print(f"❌ Direct API approach failed: {e}")
    
    def analyze_comprehensive(self, video_id: str):
        """Run comprehensive analysis using multiple approaches"""
        print(f"\n🔬 COMPREHENSIVE ANALYSIS FOR VIDEO: {video_id}")
        print("="*80)
        
        # Approach 1: Standard page analysis
        try:
            html = self.get_video_html(video_id)
            print(f"📊 Standard page HTML length: {len(html)} chars")
            
            # Save properly encoded HTML
            with open(f'debug_standard_{video_id}.html', 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"✅ Standard HTML saved as debug_standard_{video_id}.html")
            
            # Look for any JSON-like structures
            json_patterns = [
                r'var ytInitialData = ({.*?});',
                r'ytInitialPlayerResponse\s*=\s*({.*?});',
                r'ytcfg\.set\s*\(\s*({.*?})\s*\)',
                r'"responseContext":\s*({.*?"visitorData"[^}]*})',
            ]
            
            found_configs = False
            for i, pattern in enumerate(json_patterns):
                matches = re.findall(pattern, html, re.DOTALL)
                if matches:
                    found_configs = True
                    print(f"✅ Found JSON config pattern {i+1}: {len(matches)} match(es)")
                    for j, match in enumerate(matches[:2]):
                        print(f"   Config {j+1} length: {len(match)} chars")
                        # Try to extract any API-related info
                        if 'api' in match.lower() or 'key' in match.lower():
                            api_matches = re.findall(r'"[^"]*(?:api|key)[^"]*":\s*"([^"]+)"', match, re.IGNORECASE)
                            if api_matches:
                                print(f"   Potential API data: {api_matches[:5]}...")  # Show first 5
            
            if not found_configs:
                print("❌ No JSON configuration objects found")
        
        except Exception as e:
            print(f"❌ Standard page analysis failed: {e}")
        
        # Approach 2: Embedded player
        self.try_embedded_player(video_id)
        
        # Approach 3: Mobile approach
        self.try_mobile_approach(video_id)
        
        # Approach 4: Direct API call
        api_result = self.try_direct_innertube()
        if api_result:
            return api_result
        
        print(f"\n⚠️  All approaches completed. Check saved HTML files for manual inspection.")

def main():
    """Run comprehensive debugging"""
    debugger = YouTubeAdvancedDebugger()
    
    # Focus on one video first
    video_id = 'wIwCTQZ_xFE'  # Original failing video
    result = debugger.analyze_comprehensive(video_id)
    
    if result:
        print(f"\n✅ SUCCESS! Found working approach.")
        print(f"Result type: {type(result)}")
        if isinstance(result, dict):
            print(f"Result keys: {list(result.keys())}")

if __name__ == "__main__":
    main()
