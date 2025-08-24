#!/usr/bin/env python3
"""Quick debug script to test XML fetching and parsing"""

import requests
import json
from main import YouTubeTranscriptExtractor

def test_xml_fetching():
    extractor = YouTubeTranscriptExtractor()
    video_id = "wIwCTQZ_xFE"
    
    print("Getting API key...")
    api_key = extractor.get_api_key_from_homepage()
    print(f"API key: {api_key[:15]}...")
    
    print("Calling Innertube API...")
    data = extractor.call_innertube_api(video_id, api_key)
    
    print("Getting caption tracks...")
    tracks = extractor.extract_caption_tracks(data)
    
    # Show track details
    for i, track in enumerate(tracks[:3]):  # First 3 tracks
        print(f"\nTrack {i+1}:")
        print(f"  Language: {track.get('languageCode')}")
        print(f"  Name: {track.get('name', {})}")
        print(f"  Kind: {track.get('kind')}")
        print(f"  BaseUrl: {track.get('baseUrl', '')[:100]}...")
        
        if i == 0:  # Test first track
            print(f"\nTesting XML fetch for track 1:")
            try:
                xml_content = extractor.fetch_transcript_xml(track['baseUrl'])
                print(f"XML length: {len(xml_content)}")
                print(f"First 300 chars: {xml_content[:300]}")
                
                # Try parsing
                segments = extractor.parse_xml_transcript(xml_content)
                print(f"Parsed segments: {len(segments)}")
                if segments:
                    print(f"First segment: {segments[0]}")
                    
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    test_xml_fetching()
