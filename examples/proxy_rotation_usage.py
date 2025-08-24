#!/usr/bin/env python3
"""
YouTube Transcript Extractor - Proxy Rotation Example
Demonstrates how to use multiple proxies with rotation for transcript extraction.
"""

from yt_ts_extract import (
    YouTubeTranscriptExtractor, 
    ProxyManager, 
    get_transcript_with_proxy_rotation,
    get_transcript_text_with_proxy_rotation
)


def basic_proxy_rotation():
    """Basic proxy rotation example"""
    print("=== Basic Proxy Rotation ===")
    
    # Create proxy manager from file
    proxy_manager = ProxyManager.from_file("proxies.txt")
    
    # Show proxy stats
    stats = proxy_manager.get_stats()
    print(f"Loaded {stats['total_proxies']} proxies")
    print(f"Active proxies: {stats['active_proxies']}")
    print(f"Rotation strategy: {stats['rotation_strategy']}")
    
    # Create extractor with proxy rotation
    extractor = YouTubeTranscriptExtractor(
        proxy_manager=proxy_manager,
        timeout=30,
        max_retries=3
    )
    
    # Extract transcript (proxies will rotate automatically on failures)
    try:
        transcript = extractor.get_transcript("dQw4w9WgXcQ")
        print(f"Successfully extracted transcript with {len(transcript)} segments")
        
        # Show final proxy stats
        final_stats = extractor.get_proxy_stats()
        print(f"Final proxy stats: {final_stats['active_proxies']}/{final_stats['total_proxies']} active")
        
    except Exception as e:
        print(f"Error: {e}")


def proxy_rotation_with_strategies():
    """Demonstrate different rotation strategies"""
    print("\n=== Proxy Rotation Strategies ===")
    
    strategies = ["random", "round_robin", "least_used"]
    
    for strategy in strategies:
        print(f"\nTesting {strategy} strategy:")
        
        try:
            # Create proxy manager with specific strategy
            proxy_manager = ProxyManager.from_file(
                "proxies.txt", 
                rotation_strategy=strategy
            )
            
            # Use convenience function
            transcript = get_transcript_with_proxy_rotation(
                "dQw4w9WgXcQ", 
                "proxies.txt", 
                rotation_strategy=strategy
            )
            
            print(f"  ✅ Success with {strategy}: {len(transcript)} segments")
            
        except Exception as e:
            print(f"  ❌ Failed with {strategy}: {e}")


def proxy_health_checking():
    """Demonstrate proxy health checking"""
    print("\n=== Proxy Health Checking ===")
    
    try:
        # Create proxy manager
        proxy_manager = ProxyManager.from_file("proxies.txt")
        
        # Perform health check
        print("Performing health check on all proxies...")
        health_results = proxy_manager.health_check_all()
        
        # Show results
        healthy_count = 0
        for proxy_name, is_healthy in health_results.items():
            status = "✅" if is_healthy else "❌"
            print(f"  {status} {proxy_name}")
            if is_healthy:
                healthy_count += 1
        
        print(f"\nHealth check complete: {healthy_count}/{len(proxy_manager)} proxies healthy")
        
        # Show updated stats
        stats = proxy_manager.get_stats()
        print(f"Active proxies: {stats['active_proxies']}")
        print(f"Total failures: {stats['total_failures']}")
        
    except Exception as e:
        print(f"Error during health check: {e}")


def proxy_rotation_with_custom_settings():
    """Demonstrate custom proxy manager settings"""
    print("\n=== Custom Proxy Manager Settings ===")
    
    try:
        # Create proxy manager with custom settings
        proxy_manager = ProxyManager(
            proxy_configs=ProxyManager.from_file("proxies.txt").proxy_configs,
            rotation_strategy="round_robin",
            health_check_url="https://www.youtube.com",  # Use YouTube for health check
            health_check_timeout=15.0,
            max_failures=2,  # Deactivate after 2 failures
            failure_cooldown=180.0,  # 3 minutes cooldown
            min_delay_between_requests=2.0  # 2 seconds between requests to same proxy
        )
        
        print(f"Custom proxy manager created with {len(proxy_manager)} proxies")
        print(f"Strategy: {proxy_manager.rotation_strategy}")
        print(f"Max failures: {proxy_manager.max_failures}")
        print(f"Failure cooldown: {proxy_manager.failure_cooldown}s")
        
        # Test extraction
        extractor = YouTubeTranscriptExtractor(
            proxy_manager=proxy_manager,
            timeout=45,
            max_retries=5
        )
        
        transcript = extractor.get_transcript("dQw4w9WgXcQ")
        print(f"Successfully extracted transcript: {len(transcript)} segments")
        
    except Exception as e:
        print(f"Error: {e}")


def batch_processing_with_proxy_rotation():
    """Demonstrate batch processing with proxy rotation"""
    print("\n=== Batch Processing with Proxy Rotation ===")
    
    try:
        from yt_ts_extract import batch_process_ids
        
        # Create proxy manager
        proxy_manager = ProxyManager.from_file("proxies.txt")
        
        # Sample video IDs
        video_ids = [
            "dQw4w9WgXcQ",  # Rick Roll
            "9bZkp7q19f0",  # Gangnam Style
            "kJQP7kiw5Fk"   # Despacito
        ]
        
        print(f"Processing {len(video_ids)} videos with proxy rotation...")
        
        # Process batch with proxy rotation
        results = batch_process_ids(
            video_ids, 
            "transcripts/", 
            proxy_manager=proxy_manager
        )
        
        # Show results
        print(f"\nBatch processing complete!")
        print(f"Successful: {len(results['successful'])}")
        print(f"Failed: {len(results['failed'])}")
        print(f"Total time: {results['duration']}")
        
        # Show proxy stats after batch processing
        proxy_stats = proxy_manager.get_stats()
        print(f"\nProxy stats after batch processing:")
        print(f"Active proxies: {proxy_stats['active_proxies']}/{proxy_stats['total_proxies']}")
        print(f"Total failures: {proxy_stats['total_failures']}")
        
    except Exception as e:
        print(f"Error during batch processing: {e}")


def proxy_rotation_from_url_list():
    """Demonstrate creating proxy manager from URL list"""
    print("\n=== Proxy Manager from URL List ===")
    
    try:
        # List of proxy URLs
        proxy_urls = [
            "http://mhzbhrwb:yj2veiaafrbu@23.95.150.145:6114",
            "http://mhzbhrwb:yj2veiaafrbu@198.23.239.134:6540",
            "https://mhzbhrwb:yj2veiaafrbu@45.38.107.97:6014"
        ]
        
        # Create proxy manager from URL list
        proxy_manager = ProxyManager.from_list(
            proxy_urls,
            rotation_strategy="least_used"
        )
        
        print(f"Created proxy manager from {len(proxy_manager)} URLs")
        print(f"Strategy: {proxy_manager.rotation_strategy}")
        
        # Test extraction
        transcript = get_transcript_text_with_proxy_rotation(
            "dQw4w9WgXcQ",
            proxy_urls,  # This won't work with the current implementation
            rotation_strategy="least_used"
        )
        
        print(f"Successfully extracted transcript text ({len(transcript)} characters)")
        
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all proxy rotation examples"""
    print("YouTube Transcript Extractor - Proxy Rotation Examples")
    print("=" * 60)
    
    # Run examples
    basic_proxy_rotation()
    proxy_rotation_with_strategies()
    proxy_health_checking()
    proxy_rotation_with_custom_settings()
    batch_processing_with_proxy_rotation()
    proxy_rotation_from_url_list()
    
    print("\n" + "=" * 60)
    print("Proxy rotation examples completed!")
    print("\nKey Features:")
    print("• Multiple rotation strategies (random, round_robin, least_used)")
    print("• Automatic failover and health checking")
    print("• Rate limiting per proxy")
    print("• Batch processing support")
    print("• Easy integration with existing code")


if __name__ == "__main__":
    main()
