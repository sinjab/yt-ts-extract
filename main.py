#!/usr/bin/env python3
"""
YouTube Transcript Extractor using Python Requests
Enhanced implementation for 2024-2025 YouTube anti-bot systems
"""

import requests
import re
import json
import xml.etree.ElementTree as ET
from html import unescape
import time
from random import uniform
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class YouTubeTranscriptExtractor:
    """
    YouTube transcript extractor using the Innertube API approach.
    Handles 2024-2025 anti-bot systems with proper headers and rate limiting.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.last_request_time = 0
        self.min_delay = 2  # Minimum seconds between requests
        
        # Essential headers to mimic legitimate browser requests
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
        })
        
        # Ensure automatic gzip decompression
        self.session.headers['Accept-Encoding'] = 'gzip, deflate, br'
    
    def _wait_if_needed(self):
        """Implement rate limiting to avoid being blocked"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_delay:
            delay = self.min_delay - elapsed + uniform(0, 1)
            logger.debug(f"Rate limiting: waiting {delay:.2f} seconds")
            time.sleep(delay)
        self.last_request_time = time.time()
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from various YouTube URL formats"""
        patterns = [
            r'(?:v=|/)([0-9A-Za-z_-]{11}).*',
            r'youtu\.be/([0-9A-Za-z_-]{11})',
            r'embed/([0-9A-Za-z_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        raise ValueError("Invalid YouTube URL")
    
    def get_video_html(self, video_id: str) -> str:
        """Fetch YouTube video page HTML"""
        self._wait_if_needed()
        
        url = f"https://www.youtube.com/watch?v={video_id}"
        logger.info(f"Fetching video page for ID: {video_id}")
        
        try:
            response = self.session.get(url, timeout=30)
            
            # Check for blocks
            if 'recaptcha' in response.text.lower():
                raise Exception(f"IP blocked (reCAPTCHA) for video {video_id}")
            
            response.raise_for_status()
            logger.debug(f"Successfully fetched video page ({len(response.text)} chars)")
            return response.text
            
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch video page: {e}")
    
    def get_api_key_from_homepage(self) -> str:
        """Get API key using known working key"""
        logger.info("Using known working API key")
        return "AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8"
    
    def call_innertube_api(self, video_id: str, api_key: str) -> dict:
        """Call YouTube's Innertube API using Android client"""
        self._wait_if_needed()
        
        url = f"https://www.youtube.com/youtubei/v1/player?key={api_key}"
        
        # Use a fresh request session for the API call with Android headers
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'com.google.android.youtube/20.10.38 (Linux; U; Android 14) gzip',
            'X-YouTube-Client-Name': '3',  # Android client
            'X-YouTube-Client-Version': '20.10.38',
            'Accept-Encoding': 'gzip, deflate',  # Ensure requests handles decompression
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
        
        logger.info("Calling Innertube API with Android client")
        try:
            # Use a fresh requests call instead of self.session to avoid header conflicts
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Debug: Check response
            if not response.text.strip():
                raise Exception("Empty response from Innertube API")
            
            try:
                return response.json()
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error. Response length: {len(response.text)}")
                logger.error(f"Response encoding: {response.encoding}")
                logger.error(f"Content-Type: {response.headers.get('Content-Type')}")
                logger.error(f"First 200 chars: {repr(response.text[:200])}")
                raise Exception(f"Invalid JSON response from Innertube API: {e}")
                
        except requests.RequestException as e:
            raise Exception(f"Failed to call Innertube API: {e}")
    
    def extract_caption_tracks(self, innertube_data: dict) -> List[Dict]:
        """Extract caption track URLs from Innertube response"""
        # Verify video is playable
        status = innertube_data.get("playabilityStatus", {}).get("status")
        if status == "LOGIN_REQUIRED":
            raise Exception("Video requires login (age restricted)")
        elif status == "UNPLAYABLE":
            raise Exception("Video is unplayable")
        elif status != "OK":
            raise Exception(f"Video unplayable: {status}")
        
        # Get caption tracks
        captions = innertube_data.get("captions", {}).get("playerCaptionsTracklistRenderer", {})
        tracks = captions.get("captionTracks", [])
        
        if not tracks:
            raise Exception("No transcripts available for this video")
        
        logger.info(f"Found {len(tracks)} caption tracks")
        for i, track in enumerate(tracks):
            lang = track.get('languageCode', 'unknown')
            name = track.get('name', {}).get('simpleText', 'Unknown')
            track_type = 'auto-generated' if track.get('kind') == 'asr' else 'manual'
            logger.info(f"  Track {i+1}: {name} ({lang}) - {track_type}")
        
        return tracks
    
    def fetch_transcript_xml(self, url: str) -> str:
        """Fetch transcript XML from timedtext URL"""
        self._wait_if_needed()
        
        logger.debug(f"Fetching transcript XML from: {url[:100]}...")
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch transcript XML: {e}")
    
    def parse_xml_transcript(self, xml_content: str) -> List[Dict]:
        """Parse XML transcript into structured data"""
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            raise Exception(f"Failed to parse transcript XML: {e}")
        
        segments = []
        
        # Try different XML formats
        # Format 1: <text> elements (older format)
        text_elements = root.findall('.//text')
        if text_elements:
            for text_elem in text_elements:
                start = float(text_elem.get('start', 0))
                duration = float(text_elem.get('dur', 0))
                text = text_elem.text or ''
                
                # Clean text
                text = unescape(text).strip()
                text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
                text = re.sub(r'\s+', ' ', text)    # Normalize whitespace
                
                if text:
                    segments.append({
                        'text': text,
                        'start': start,
                        'duration': duration,
                        'end': start + duration
                    })
        
        # Format 2: <p> elements (newer format, like in our debug)
        else:
            p_elements = root.findall('.//p')
            for p_elem in p_elements:
                # Get timing from <p> element
                start_ms = p_elem.get('t')  # milliseconds
                duration_ms = p_elem.get('d')  # milliseconds
                
                if start_ms is not None:
                    start = float(start_ms) / 1000.0  # convert to seconds
                    duration = float(duration_ms) / 1000.0 if duration_ms else 0
                    
                    # Extract text from <s> elements or direct text
                    text_parts = []
                    s_elements = p_elem.findall('.//s')
                    
                    if s_elements:
                        # Extract text from <s> elements
                        for s_elem in s_elements:
                            if s_elem.text:
                                text_parts.append(s_elem.text.strip())
                    else:
                        # Fallback: get all text content
                        if p_elem.text:
                            text_parts.append(p_elem.text.strip())
                        for child in p_elem:
                            if child.text:
                                text_parts.append(child.text.strip())
                            if child.tail:
                                text_parts.append(child.tail.strip())
                    
                    # Join and clean text
                    text = ' '.join(text_parts).strip()
                    text = unescape(text)
                    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
                    text = re.sub(r'\s+', ' ', text)    # Normalize whitespace
                    
                    if text:
                        segments.append({
                            'text': text,
                            'start': start,
                            'duration': duration,
                            'end': start + duration
                        })
        
        logger.info(f"Parsed {len(segments)} transcript segments")
        return segments
    
    def get_available_languages(self, video_url: str) -> List[Dict]:
        """Get list of available transcript languages for a video"""
        video_id = self.extract_video_id(video_url)
        api_key = self.get_api_key_from_homepage()
        data = self.call_innertube_api(video_id, api_key)
        tracks = self.extract_caption_tracks(data)
        
        languages = []
        for track in tracks:
            languages.append({
                'code': track.get('languageCode'),
                'name': track.get('name', {}).get('simpleText', 'Unknown'),
                'auto_generated': track.get('kind') == 'asr'
            })
        
        return languages
    
    def get_transcript(self, video_url: str, language: str = 'en', 
                      prefer_manual: bool = True) -> List[Dict]:
        """
        Main method to extract transcript
        
        Args:
            video_url: YouTube video URL
            language: Language code (e.g., 'en', 'es', 'fr')
            prefer_manual: Prefer manual transcripts over auto-generated
        
        Returns:
            List of transcript segments with text, start, duration, and end times
        """
        video_id = self.extract_video_id(video_url)
        logger.info(f"Extracting transcript for video: {video_id}")
        
        try:
            # Step 1: Get API key from homepage (more reliable)
            api_key = self.get_api_key_from_homepage()
            
            # Step 2: Call Innertube API with Android client
            data = self.call_innertube_api(video_id, api_key)
            
            # Step 3: Extract caption tracks
            tracks = self.extract_caption_tracks(data)
            
            # Step 4: Find desired language track
            selected_track = self._select_best_track(tracks, language, prefer_manual)
            
            if not selected_track:
                available = [t.get('languageCode', 'unknown') for t in tracks]
                raise Exception(f"No transcript available for language '{language}'. Available: {available}")
            
            # Step 5: Fetch and parse transcript
            logger.info(f"Selected track: {selected_track.get('name', {}).get('simpleText', 'Unknown')}")
            xml_content = self.fetch_transcript_xml(selected_track['baseUrl'])
            transcript = self.parse_xml_transcript(xml_content)
            
            logger.info("Transcript extraction completed successfully")
            return transcript
            
        except Exception as e:
            logger.error(f"Failed to extract transcript: {e}")
            raise
    
    def _select_best_track(self, tracks: List[Dict], language: str, 
                          prefer_manual: bool) -> Optional[Dict]:
        """Select the best caption track based on language and preference"""
        matching_tracks = [t for t in tracks if t.get('languageCode') == language]
        
        if not matching_tracks:
            # Fallback to first available track
            if tracks:
                logger.warning(f"Language '{language}' not found, using first available track")
                return tracks[0]
            return None
        
        if prefer_manual:
            # Look for manual transcript first (no 'kind' field or kind != 'asr')
            manual_tracks = [t for t in matching_tracks if t.get('kind') != 'asr']
            if manual_tracks:
                return manual_tracks[0]
        
        # Return first matching track (could be auto-generated)
        return matching_tracks[0]
    
    def get_transcript_text(self, video_url: str, language: str = 'en') -> str:
        """Get transcript as a single text string"""
        segments = self.get_transcript(video_url, language)
        return ' '.join(segment['text'] for segment in segments)
    
    def get_transcript_with_timestamps(self, video_url: str, language: str = 'en') -> str:
        """Get transcript formatted with timestamps"""
        segments = self.get_transcript(video_url, language)
        formatted_lines = []
        
        for segment in segments:
            timestamp = self._format_timestamp(segment['start'])
            formatted_lines.append(f"[{timestamp}] {segment['text']}")
        
        return '\n'.join(formatted_lines)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds as MM:SS or HH:MM:SS"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"


def main():
    """Example usage and testing"""
    extractor = YouTubeTranscriptExtractor()
    
    # Test with a known video (replace with actual video URL)
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
        "https://youtu.be/dQw4w9WgXcQ",                 # Short format
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing URL: {url}")
        print('='*60)
        
        try:
            # Get available languages
            print("\nAvailable languages:")
            languages = extractor.get_available_languages(url)
            for lang in languages:
                status = "auto-generated" if lang['auto_generated'] else "manual"
                print(f"  - {lang['name']} ({lang['code']}) [{status}]")
            
            # Get transcript
            print("\nExtracting transcript...")
            transcript = extractor.get_transcript(url, language='en')
            
            # Display first 5 segments
            print(f"\nFirst 5 segments (out of {len(transcript)}):")
            for i, segment in enumerate(transcript[:5]):
                timestamp = extractor._format_timestamp(segment['start'])
                print(f"  [{timestamp}] {segment['text']}")
            
            # Get full text version
            print("\nFirst 200 characters of full text:")
            full_text = extractor.get_transcript_text(url)
            print(f"  {full_text[:200]}...")
            
            break  # Success, exit loop
            
        except Exception as e:
            print(f"Error: {e}")
            print("Trying next URL...")
            continue
    
    print(f"\n{'='*60}")
    print("Test completed!")


if __name__ == "__main__":
    main()
