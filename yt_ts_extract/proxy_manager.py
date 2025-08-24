#!/usr/bin/env python3
"""
YouTube Transcript Extractor - Proxy Manager
Handles multiple proxies with rotation, load balancing, and health checking.
"""

import random
import time
import requests
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProxyConfig:
    """Configuration for a single proxy"""

    address: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"
    last_used: float = 0.0
    fail_count: int = 0
    last_fail_time: float = 0.0
    is_active: bool = True

    @property
    def url(self) -> str:
        """Generate proxy URL from configuration"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.address}:{self.port}"
        return f"{self.protocol}://{self.address}:{self.port}"

    @property
    def display_name(self) -> str:
        """Display name for logging (without credentials)"""
        return f"{self.protocol}://{self.address}:{self.port}"


class ProxyManager:
    """
    Manages multiple proxies with rotation, health checking, and failover.

    Features:
    - Load balancing across multiple proxies
    - Automatic failover on proxy failures
    - Health checking and recovery
    - Rate limiting per proxy
    - Random and round-robin rotation strategies
    """

    def __init__(
        self,
        proxy_configs: Optional[List[ProxyConfig]] = None,
        rotation_strategy: str = "random",
        health_check_url: str = "https://www.google.com",
        health_check_timeout: float = 10.0,
        max_failures: int = 3,
        failure_cooldown: float = 300.0,  # 5 minutes
        min_delay_between_requests: float = 1.0,
    ):
        """
        Initialize the proxy manager.

        Args:
            proxy_configs: List of proxy configurations
            rotation_strategy: "random", "round_robin", or "least_used"
            health_check_url: URL to use for health checking
            health_check_timeout: Timeout for health checks
            max_failures: Maximum failures before marking proxy as inactive
            failure_cooldown: Cooldown period after failures (seconds)
            min_delay_between_requests: Minimum delay between requests to same proxy
        """
        self.proxy_configs = proxy_configs or []
        self.rotation_strategy = rotation_strategy
        self.health_check_url = health_check_url
        self.health_check_timeout = health_check_timeout
        self.max_failures = max_failures
        self.failure_cooldown = failure_cooldown
        self.min_delay_between_requests = min_delay_between_requests

        self.current_index = 0
        self.last_rotation = time.time()

        # Validate rotation strategy
        if rotation_strategy not in ["random", "round_robin", "least_used"]:
            raise ValueError(
                f"Invalid rotation strategy: {rotation_strategy}. "
                f"Must be one of: random, round_robin, least_used"
            )

        logger.info(
            f"Initialized ProxyManager with {len(self.proxy_configs)} proxies, "
            f"strategy: {rotation_strategy}"
        )

    @classmethod
    def from_file(cls, filepath: str, **kwargs) -> "ProxyManager":
        """
        Create ProxyManager from a proxy list file.

        Expected format (space or tab separated):
        Address Port Username Password
        23.95.150.145 6114 mhzbhrwb yj2veiaafrbu
        198.23.239.134 6540 mhzbhrwb yj2veiaafrbu

        Args:
            filepath: Path to proxy list file
            **kwargs: Additional arguments for ProxyManager constructor

        Returns:
            ProxyManager instance
        """
        proxy_configs = []

        try:
            with open(filepath, "r") as f:
                lines = f.readlines()

            # Skip header line if it exists
            start_line = 0
            if lines and any(
                keyword in lines[0].lower()
                for keyword in ["address", "port", "username", "password"]
            ):
                start_line = 1

            for line_num, line in enumerate(lines[start_line:], start_line + 1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                try:
                    # Try space-separated first
                    parts = line.split()
                    if len(parts) >= 2:
                        address = parts[0]
                        port = int(parts[1])
                        username = parts[2] if len(parts) > 2 else None
                        password = parts[3] if len(parts) > 3 else None

                        # Determine protocol based on port or default to http
                        protocol = "http"
                        if port in [443, 8443]:
                            protocol = "https"
                        elif port in [1080, 1081]:
                            protocol = "socks5"

                        proxy_config = ProxyConfig(
                            address=address,
                            port=port,
                            username=username,
                            password=password,
                            protocol=protocol,
                        )
                        proxy_configs.append(proxy_config)

                except (ValueError, IndexError) as e:
                    logger.warning(f"Skipping invalid proxy line {line_num}: {line} - {e}")
                    continue

            logger.info(f"Loaded {len(proxy_configs)} proxies from {filepath}")

        except FileNotFoundError:
            raise FileNotFoundError(f"Proxy list file not found: {filepath}")
        except Exception as e:
            raise RuntimeError(f"Error reading proxy list file {filepath}: {e}")

        return cls(proxy_configs, **kwargs)

    @classmethod
    def from_list(cls, proxy_urls: List[str], **kwargs) -> "ProxyManager":
        """
        Create ProxyManager from a list of proxy URLs.

        Args:
            proxy_urls: List of proxy URLs (e.g., ["http://user:pass@host:port"])
            **kwargs: Additional arguments for ProxyManager constructor

        Returns:
            ProxyManager instance
        """
        proxy_configs = []

        for url in proxy_urls:
            try:
                # Parse proxy URL
                if url.startswith(("http://", "https://", "socks5://")):
                    protocol = url.split("://")[0]
                    rest = url.split("://")[1]

                    if "@" in rest:
                        auth, host_port = rest.split("@", 1)
                        username, password = auth.split(":", 1)
                        address, port = host_port.rsplit(":", 1)
                    else:
                        username = password = None
                        address, port = rest.rsplit(":", 1)

                    proxy_config = ProxyConfig(
                        address=address,
                        port=int(port),
                        username=username,
                        password=password,
                        protocol=protocol,
                    )
                    proxy_configs.append(proxy_config)

            except Exception as e:
                logger.warning(f"Skipping invalid proxy URL {url}: {e}")
                continue

        logger.info(f"Loaded {len(proxy_configs)} proxies from URL list")
        return cls(proxy_configs, **kwargs)

    def get_next_proxy(self) -> Optional[ProxyConfig]:
        """
        Get the next available proxy based on rotation strategy.

        Returns:
            ProxyConfig or None if no proxies available
        """
        active_proxies = [p for p in self.proxy_configs if p.is_active]

        if not active_proxies:
            logger.warning("No active proxies available")
            return None

        # Check if we need to rotate (based on time)
        current_time = time.time()
        if current_time - self.last_rotation > 60:  # Rotate every minute
            self.last_rotation = current_time

        if self.rotation_strategy == "random":
            # Random selection
            proxy = random.choice(active_proxies)

        elif self.rotation_strategy == "round_robin":
            # Round-robin selection
            proxy = active_proxies[self.current_index % len(active_proxies)]
            self.current_index = (self.current_index + 1) % len(active_proxies)

        elif self.rotation_strategy == "least_used":
            # Select proxy with oldest last_used time
            proxy = min(active_proxies, key=lambda p: p.last_used)

        else:
            # Fallback to random
            proxy = random.choice(active_proxies)

        # Check if proxy is ready for use (respecting delay)
        if current_time - proxy.last_used < self.min_delay_between_requests:
            # Try to find another proxy that's ready
            ready_proxies = [
                p
                for p in active_proxies
                if current_time - p.last_used >= self.min_delay_between_requests
            ]
            if ready_proxies:
                proxy = random.choice(ready_proxies)
            else:
                # All proxies are in cooldown, wait a bit
                time.sleep(0.1)

        proxy.last_used = current_time
        logger.debug(f"Selected proxy: {proxy.display_name}")
        return proxy

    def mark_proxy_failed(self, proxy: ProxyConfig, error: str = "Unknown error"):
        """
        Mark a proxy as failed and potentially deactivate it.

        Args:
            proxy: The proxy that failed
            error: Error description
        """
        current_time = time.time()
        proxy.fail_count += 1
        proxy.last_fail_time = current_time

        logger.warning(
            f"Proxy {proxy.display_name} failed: {error} "
            f"(failures: {proxy.fail_count}/{self.max_failures})"
        )

        if proxy.fail_count >= self.max_failures:
            proxy.is_active = False
            logger.error(
                f"Proxy {proxy.display_name} deactivated due to {proxy.fail_count} failures"
            )

    def mark_proxy_success(self, proxy: ProxyConfig):
        """Mark a proxy as successful, resetting failure count."""
        if proxy.fail_count > 0:
            proxy.fail_count = 0
            logger.info(f"Proxy {proxy.display_name} recovered from failures")

    def reactivate_proxies(self):
        """Reactivate proxies that have been in cooldown long enough."""
        current_time = time.time()
        reactivated = 0

        for proxy in self.proxy_configs:
            if not proxy.is_active and proxy.fail_count >= self.max_failures:
                if current_time - proxy.last_fail_time >= self.failure_cooldown:
                    proxy.is_active = True
                    proxy.fail_count = 0
                    reactivated += 1
                    logger.info(f"Reactivated proxy: {proxy.display_name}")

        if reactivated > 0:
            logger.info(f"Reactivated {reactivated} proxies")

    def health_check_all(self) -> Dict[str, bool]:
        """
        Perform health check on all proxies.

        Returns:
            Dictionary mapping proxy display names to health status
        """
        results = {}

        for proxy in self.proxy_configs:
            try:
                # Create a test session with this proxy
                test_session = requests.Session()
                test_session.proxies = {"http": proxy.url, "https": proxy.url}
                test_session.timeout = self.health_check_timeout

                # Test the proxy
                response = test_session.get(self.health_check_url)
                if response.status_code == 200:
                    results[proxy.display_name] = True
                    self.mark_proxy_success(proxy)
                else:
                    results[proxy.display_name] = False
                    self.mark_proxy_failed(proxy, f"HTTP {response.status_code}")

            except Exception as e:
                results[proxy.display_name] = False
                self.mark_proxy_failed(proxy, str(e))

        return results

    def get_stats(self) -> Dict:
        """Get statistics about proxy usage and health."""
        active_count = sum(1 for p in self.proxy_configs if p.is_active)
        total_failures = sum(p.fail_count for p in self.proxy_configs)

        return {
            "total_proxies": len(self.proxy_configs),
            "active_proxies": active_count,
            "inactive_proxies": len(self.proxy_configs) - active_count,
            "total_failures": total_failures,
            "rotation_strategy": self.rotation_strategy,
            "health_check_url": self.health_check_url,
        }

    def __len__(self) -> int:
        """Return the number of proxy configurations."""
        return len(self.proxy_configs)

    def __bool__(self) -> bool:
        """Return True if there are any proxy configurations."""
        return len(self.proxy_configs) > 0
