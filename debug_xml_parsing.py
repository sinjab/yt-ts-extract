#!/usr/bin/env python3
"""
Debug script to investigate XML parsing issues
"""

import logging
from main import YouTubeTranscriptExtractor

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_xml_parsing():
    extractor = YouTubeTranscriptExtractor()
    
    video_url = "https://www.youtube.com/watch?v=wIwCTQZ_xFE"
    video_id = extractor.extract_video_id(video_url)
    
    print(f"Video ID: {video_id}")
    
    try:
        # Get API key
        api_key = extractor.get_api_key_from_homepage()
        print(f"API Key: {api_key[:10]}...")
        
        # Call Innertube API
        data = extractor.call_innertube_api(video_id, api_key)
        
        # Extract caption tracks
        tracks = extractor.extract_caption_tracks(data)
        print(f"Found {len(tracks)} tracks")
        
        # Find English track
        english_tracks = [t for t in tracks if t.get('languageCode') == 'en']
        if not english_tracks:
            english_tracks = [t for t in tracks if 'en' in t.get('languageCode', '')]
        
        if english_tracks:
            track = english_tracks[0]
            print(f"Selected track: {track.get('languageCode')}")
            print(f"Track keys: {list(track.keys())}")
            
            if 'baseUrl' in track:
                # Fetch XML
                xml_content = extractor.fetch_transcript_xml(track['baseUrl'])
                print(f"XML content length: {len(xml_content)}")
                print(f"First 500 chars of XML:")
                print(xml_content[:500])
                print("---")
                
                # Try parsing
                segments = extractor.parse_xml_transcript(xml_content)
                print(f"Parsed segments: {len(segments)}")
                
                if segments:
                    print(f"First segment: {segments[0]}")
                else:
                    print("No segments found!")
                    
                    # Debug XML structure
                    import xml.etree.ElementTree as ET
                    root = ET.fromstring(xml_content)
                    print(f"Root tag: {root.tag}")
                    print(f"Root attributes: {root.attrib}")
                    
                    # Find all elements
                    for elem in root.iter():
                        print(f"Element: {elem.tag}, attributes: {elem.attrib}, text: {repr(elem.text)}")
                        if len(list(elem)) == 0:  # Leaf element
                            break
                
            else:
                print("No baseUrl found in track!")
                print(f"Track structure: {track}")
        else:
            print("No English tracks found")
            print("Available languages:")
            for track in tracks[:5]:  # Show first 5
                print(f"  {track.get('languageCode')}: {track.get('name', {}).get('simpleText', 'Unknown')}")
    
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_xml_parsing()
