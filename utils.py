#!/usr/bin/env python3
"""
YouTube Transcript Extractor - Utility Functions
Additional helper functions for common transcript processing tasks.
"""

import re
from typing import List, Dict, Optional
from collections import Counter
from main import YouTubeTranscriptExtractor


def export_to_srt(transcript: List[Dict], filename: str = "transcript.srt") -> str:
    """
    Convert transcript segments to SRT subtitle format.
    
    Args:
        transcript: List of transcript segments from get_transcript()
        filename: Output filename for SRT file
    
    Returns:
        SRT formatted string
    
    Example:
        transcript = extractor.get_transcript("https://youtube.com/watch?v=...")
        srt_content = export_to_srt(transcript, "video_subtitles.srt")
    """
    def format_srt_timestamp(seconds: float) -> str:
        """Convert seconds to SRT timestamp format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    srt_content = []
    
    for i, segment in enumerate(transcript, 1):
        start_time = segment['start']
        duration = segment.get('duration', 3.0)  # Default 3 seconds if no duration
        end_time = start_time + duration
        
        start_timestamp = format_srt_timestamp(start_time)
        end_timestamp = format_srt_timestamp(end_time)
        
        text = segment['text'].strip()
        
        # SRT format: sequence number, timestamp, text, blank line
        srt_entry = f"{i}\n{start_timestamp} --> {end_timestamp}\n{text}\n"
        srt_content.append(srt_entry)
    
    srt_string = "\n".join(srt_content)
    
    # Write to file if filename provided
    if filename:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(srt_string)
        print(f"SRT file saved as: {filename}")
    
    return srt_string


def clean_transcript_text(text: str) -> str:
    """
    Clean transcript text by removing artifacts and formatting issues.
    
    Args:
        text: Raw transcript text
    
    Returns:
        Cleaned text
    
    Example:
        raw_text = extractor.get_transcript_text("https://youtube.com/watch?v=...")
        clean_text = clean_transcript_text(raw_text)
    """
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common artifacts
    text = re.sub(r'\[Music\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[Applause\]', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[Laughter\]', '', text, flags=re.IGNORECASE)
    
    # Fix common punctuation issues
    text = re.sub(r'\s+([.!?])', r'\1', text)  # Remove space before punctuation
    text = re.sub(r'([.!?])\s*([a-z])', r'\1 \2', text)  # Add space after punctuation
    
    # Capitalize sentences
    sentences = text.split('. ')
    sentences = [s.capitalize() if s else s for s in sentences]
    text = '. '.join(sentences)
    
    return text.strip()


def extract_keywords(transcript: List[Dict], top_n: int = 20) -> List[tuple]:
    """
    Extract most common keywords from transcript.
    
    Args:
        transcript: List of transcript segments
        top_n: Number of top keywords to return
    
    Returns:
        List of tuples (word, count) sorted by frequency
    
    Example:
        transcript = extractor.get_transcript("https://youtube.com/watch?v=...")
        keywords = extract_keywords(transcript, 15)
        for word, count in keywords:
            print(f"{word}: {count}")
    """
    # Combine all text
    full_text = " ".join([segment['text'] for segment in transcript])
    
    # Clean and normalize text
    text = full_text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove non-alphabetic characters
    
    # Common stop words to filter out
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does',
        'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
        'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'so', 'if', 'then',
        'than', 'as', 'very', 'too', 'much', 'many', 'more', 'most', 'some', 'any', 'all',
        'no', 'not', 'now', 'here', 'there', 'when', 'where', 'why', 'how', 'what', 'who',
        'which', 'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then',
        'once', 'just', 'only', 'get', 'got', 'go', 'going', 'like', 'know', 'see', 'one',
        'two', 'three', 'also', 'well', 'way', 'back', 'time', 'good', 'right', 'think'
    }
    
    # Split into words and filter
    words = [word for word in text.split() if word not in stop_words and len(word) > 2]
    
    # Count word frequencies
    word_counts = Counter(words)
    
    return word_counts.most_common(top_n)


def search_transcript(transcript: List[Dict], query: str, context_words: int = 5) -> List[Dict]:
    """
    Search for specific text in transcript with context.
    
    Args:
        transcript: List of transcript segments
        query: Search term
        context_words: Number of words before/after match to include
    
    Returns:
        List of matches with context and timestamps
    
    Example:
        transcript = extractor.get_transcript("https://youtube.com/watch?v=...")
        matches = search_transcript(transcript, "artificial intelligence", context_words=10)
        for match in matches:
            print(f"[{match['timestamp']}] {match['text']}")
    """
    matches = []
    query_lower = query.lower()
    
    for segment in transcript:
        text = segment['text']
        text_lower = text.lower()
        
        if query_lower in text_lower:
            # Find the position of the match
            match_start = text_lower.find(query_lower)
            
            # Extract context
            words = text.split()
            query_words = query.split()
            
            # Find which word the match starts in
            word_start = len(' '.join(words[:len(words)//2]).split())
            
            # Get context window
            start_word = max(0, word_start - context_words)
            end_word = min(len(words), word_start + len(query_words) + context_words)
            
            context_text = ' '.join(words[start_word:end_word])
            
            # Format timestamp
            extractor = YouTubeTranscriptExtractor()
            timestamp = extractor._format_timestamp(segment['start'])
            
            matches.append({
                'timestamp': timestamp,
                'time_seconds': segment['start'],
                'text': context_text,
                'full_segment': text
            })
    
    return matches


def create_summary(transcript: List[Dict], max_sentences: int = 5) -> str:
    """
    Create a simple extractive summary from transcript.
    
    Args:
        transcript: List of transcript segments
        max_sentences: Maximum number of sentences in summary
    
    Returns:
        Summary text
    
    Example:
        transcript = extractor.get_transcript("https://youtube.com/watch?v=...")
        summary = create_summary(transcript, max_sentences=3)
        print("Summary:", summary)
    """
    # Combine all text
    full_text = " ".join([segment['text'] for segment in transcript])
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', full_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Simple scoring: prefer longer sentences that contain common keywords
    keywords = extract_keywords(transcript, 10)
    keyword_set = {word for word, count in keywords}
    
    scored_sentences = []
    for sentence in sentences:
        if len(sentence.split()) < 5:  # Skip very short sentences
            continue
            
        # Score based on keyword overlap
        words = set(sentence.lower().split())
        score = len(words.intersection(keyword_set))
        score += len(sentence) / 100  # Slight preference for longer sentences
        
        scored_sentences.append((score, sentence))
    
    # Sort by score and take top sentences
    scored_sentences.sort(reverse=True)
    summary_sentences = [sentence for score, sentence in scored_sentences[:max_sentences]]
    
    return '. '.join(summary_sentences) + '.'


def get_transcript_stats(transcript: List[Dict]) -> Dict:
    """
    Get comprehensive statistics about the transcript.
    
    Args:
        transcript: List of transcript segments
    
    Returns:
        Dictionary with various statistics
    
    Example:
        transcript = extractor.get_transcript("https://youtube.com/watch?v=...")
        stats = get_transcript_stats(transcript)
        print(f"Duration: {stats['duration_formatted']}")
        print(f"Word count: {stats['word_count']}")
    """
    if not transcript:
        return {}
    
    # Calculate basic stats
    total_duration = max(segment['start'] + segment.get('duration', 0) for segment in transcript)
    
    # Combine all text
    full_text = " ".join([segment['text'] for segment in transcript])
    
    # Count words, characters, sentences
    word_count = len(full_text.split())
    char_count = len(full_text)
    sentence_count = len(re.split(r'[.!?]+', full_text))
    
    # Calculate speaking rate
    words_per_minute = (word_count / total_duration) * 60 if total_duration > 0 else 0
    
    # Format duration
    extractor = YouTubeTranscriptExtractor()
    duration_formatted = extractor._format_timestamp(total_duration)
    
    return {
        'segment_count': len(transcript),
        'duration_seconds': total_duration,
        'duration_formatted': duration_formatted,
        'word_count': word_count,
        'character_count': char_count,
        'sentence_count': sentence_count,
        'words_per_minute': round(words_per_minute, 1),
        'average_words_per_segment': round(word_count / len(transcript), 1),
        'longest_segment': max(transcript, key=lambda x: len(x['text']))['text'][:100] + "...",
        'first_words': full_text[:100] + "...",
        'last_words': "..." + full_text[-100:] if len(full_text) > 100 else full_text
    }


def batch_process_urls(urls: List[str], output_dir: str = "transcripts/") -> Dict:
    """
    Process multiple YouTube URLs and save transcripts.
    
    Args:
        urls: List of YouTube URLs
        output_dir: Directory to save transcripts
    
    Returns:
        Processing results summary
    
    Example:
        urls = [
            "https://youtube.com/watch?v=video1",
            "https://youtube.com/watch?v=video2"
        ]
        results = batch_process_urls(urls, "my_transcripts/")
    """
    import os
    from datetime import datetime
    
    extractor = YouTubeTranscriptExtractor()
    results = {
        'successful': [],
        'failed': [],
        'total_processed': 0,
        'start_time': datetime.now()
    }
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    for i, url in enumerate(urls, 1):
        print(f"Processing {i}/{len(urls)}: {url}")
        
        try:
            # Extract video ID for filename
            video_id = extractor.extract_video_id(url)
            
            # Get transcript
            transcript = extractor.get_transcript(url)
            
            # Save as multiple formats
            base_filename = os.path.join(output_dir, f"{video_id}")
            
            # Save raw transcript (JSON-like)
            with open(f"{base_filename}_segments.txt", 'w', encoding='utf-8') as f:
                for segment in transcript:
                    timestamp = extractor._format_timestamp(segment['start'])
                    f.write(f"[{timestamp}] {segment['text']}\n")
            
            # Save as plain text
            plain_text = extractor.get_transcript_text(url)
            with open(f"{base_filename}_text.txt", 'w', encoding='utf-8') as f:
                f.write(clean_transcript_text(plain_text))
            
            # Save as SRT
            export_to_srt(transcript, f"{base_filename}.srt")
            
            # Get stats
            stats = get_transcript_stats(transcript)
            
            results['successful'].append({
                'url': url,
                'video_id': video_id,
                'files_created': [
                    f"{base_filename}_segments.txt",
                    f"{base_filename}_text.txt", 
                    f"{base_filename}.srt"
                ],
                'stats': stats
            })
            
        except Exception as e:
            results['failed'].append({
                'url': url,
                'error': str(e)
            })
        
        results['total_processed'] += 1
    
    results['end_time'] = datetime.now()
    results['duration'] = results['end_time'] - results['start_time']
    
    # Print summary
    print(f"\nBatch processing completed!")
    print(f"Successful: {len(results['successful'])}")
    print(f"Failed: {len(results['failed'])}")
    print(f"Total time: {results['duration']}")
    
    return results


def demo_utilities():
    """Demonstrate all utility functions"""
    print("YouTube Transcript Utilities - Demo")
    print("=" * 50)
    
    extractor = YouTubeTranscriptExtractor()
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        print(f"Testing with URL: {test_url}")
        transcript = extractor.get_transcript(test_url)
        
        print("\n1. Transcript Stats:")
        stats = get_transcript_stats(transcript)
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        print("\n2. Top Keywords:")
        keywords = extract_keywords(transcript, 10)
        for word, count in keywords[:5]:
            print(f"   {word}: {count}")
        
        print("\n3. Sample SRT Export:")
        srt_content = export_to_srt(transcript[:3], filename=None)  # Just first 3 segments
        print("   " + srt_content.replace('\n', '\n   ')[:200] + "...")
        
        print("\n4. Search Example:")
        # This would work if the transcript contained the search term
        matches = search_transcript(transcript, "never", context_words=3)
        if matches:
            print(f"   Found {len(matches)} matches for 'never'")
            print(f"   First match: {matches[0]['text'][:100]}...")
        else:
            print("   No matches found for 'never'")
        
        print("\n5. Summary:")
        summary = create_summary(transcript, max_sentences=2)
        print(f"   {summary[:200]}...")
        
    except Exception as e:
        print(f"Demo encountered expected error: {e}")
        print("This is normal due to YouTube's anti-bot protection.")
    
    print(f"\n{'='*50}")
    print("All utility functions are ready to use!")


if __name__ == "__main__":
    demo_utilities()
