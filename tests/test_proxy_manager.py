#!/usr/bin/env python3
"""
Tests for ProxyManager and ProxyConfig classes
"""

import pytest
import tempfile
import os
import time
from unittest.mock import patch, MagicMock
from yt_ts_extract.proxy_manager import ProxyManager, ProxyConfig


class TestProxyConfig:
    """Test ProxyConfig dataclass"""

    def test_proxy_config_basic(self):
        """Test basic ProxyConfig creation"""
        config = ProxyConfig(address="192.168.1.1", port=8080, username="user", password="pass")

        assert config.address == "192.168.1.1"
        assert config.port == 8080
        assert config.username == "user"
        assert config.password == "pass"
        assert config.protocol == "http"
        assert config.is_active is True
        assert config.fail_count == 0

    def test_proxy_config_without_auth(self):
        """Test ProxyConfig without authentication"""
        config = ProxyConfig(address="192.168.1.1", port=8080)

        assert config.username is None
        assert config.password is None
        assert config.protocol == "http"

    def test_proxy_config_custom_protocol(self):
        """Test ProxyConfig with custom protocol"""
        config = ProxyConfig(address="192.168.1.1", port=1080, protocol="socks5")

        assert config.protocol == "socks5"

    def test_proxy_url_with_auth(self):
        """Test proxy URL generation with authentication"""
        config = ProxyConfig(address="192.168.1.1", port=8080, username="user", password="pass")

        expected = "http://user:pass@192.168.1.1:8080"
        assert config.url == expected

    def test_proxy_url_without_auth(self):
        """Test proxy URL generation without authentication"""
        config = ProxyConfig(address="192.168.1.1", port=8080)

        expected = "http://192.168.1.1:8080"
        assert config.url == expected

    def test_display_name(self):
        """Test display name generation"""
        config = ProxyConfig(address="192.168.1.1", port=8080, username="user", password="pass")

        expected = "http://192.168.1.1:8080"
        assert config.display_name == expected


class TestProxyManager:
    """Test ProxyManager class"""

    def test_proxy_manager_init(self):
        """Test ProxyManager initialization"""
        manager = ProxyManager()
        assert len(manager.proxy_configs) == 0
        assert manager.rotation_strategy == "random"
        assert manager.health_check_url == "https://www.google.com"

    def test_proxy_manager_with_configs(self):
        """Test ProxyManager with proxy configurations"""
        configs = [ProxyConfig("192.168.1.1", 8080), ProxyConfig("192.168.1.2", 8080)]

        manager = ProxyManager(proxy_configs=configs)
        assert len(manager) == 2
        assert manager.proxy_configs == configs

    def test_proxy_manager_invalid_strategy(self):
        """Test ProxyManager with invalid rotation strategy"""
        with pytest.raises(ValueError, match="Invalid rotation strategy"):
            ProxyManager(rotation_strategy="invalid")

    def test_proxy_manager_from_file(self, tmp_path):
        """Test creating ProxyManager from file"""
        proxy_file = tmp_path / "proxies.txt"
        proxy_file.write_text(
            """Address Port Username Password
192.168.1.1 8080 user1 pass1
192.168.1.2 8080 user2 pass2
# Comment line
192.168.1.3 8080 user3 pass3"""
        )

        manager = ProxyManager.from_file(str(proxy_file))
        assert len(manager) == 3

        # Check first proxy
        first_proxy = manager.proxy_configs[0]
        assert first_proxy.address == "192.168.1.1"
        assert first_proxy.port == 8080
        assert first_proxy.username == "user1"
        assert first_proxy.password == "pass1"

    def test_proxy_manager_from_file_without_header(self, tmp_path):
        """Test creating ProxyManager from file without header"""
        proxy_file = tmp_path / "proxies.txt"
        proxy_file.write_text(
            """192.168.1.1 8080 user1 pass1
192.168.1.2 8080 user2 pass2"""
        )

        manager = ProxyManager.from_file(str(proxy_file))
        assert len(manager) == 2

    def test_proxy_manager_from_file_invalid_line(self, tmp_path):
        """Test creating ProxyManager from file with invalid lines"""
        proxy_file = tmp_path / "proxies.txt"
        proxy_file.write_text(
            """Address Port Username Password
192.168.1.1 8080 user1 pass1
invalid line
192.168.1.2 8080 user2 pass2"""
        )

        manager = ProxyManager.from_file(str(proxy_file))
        assert len(manager) == 2  # Invalid line should be skipped

    def test_proxy_manager_from_file_not_found(self):
        """Test creating ProxyManager from non-existent file"""
        with pytest.raises(FileNotFoundError):
            ProxyManager.from_file("nonexistent.txt")

    def test_proxy_manager_from_list(self):
        """Test creating ProxyManager from URL list"""
        urls = [
            "http://user1:pass1@192.168.1.1:8080",
            "https://192.168.1.2:8443",
            "socks5://user2:pass2@192.168.1.3:1080",
        ]

        manager = ProxyManager.from_list(urls)
        assert len(manager) == 3

        # Check protocols
        assert manager.proxy_configs[0].protocol == "http"
        assert manager.proxy_configs[1].protocol == "https"
        assert manager.proxy_configs[2].protocol == "socks5"

    def test_proxy_manager_from_list_invalid_url(self):
        """Test creating ProxyManager from list with invalid URLs"""
        urls = ["http://user1:pass1@192.168.1.1:8080", "invalid-url", "https://192.168.1.2:8443"]

        manager = ProxyManager.from_list(urls)
        assert len(manager) == 2  # Invalid URL should be skipped

    def test_get_next_proxy_random(self):
        """Test random proxy selection"""
        configs = [
            ProxyConfig("192.168.1.1", 8080),
            ProxyConfig("192.168.1.2", 8080),
            ProxyConfig("192.168.1.3", 8080),
        ]

        manager = ProxyManager(proxy_configs=configs, rotation_strategy="random")

        # Test multiple selections
        proxies = set()
        for _ in range(10):
            proxy = manager.get_next_proxy()
            proxies.add(proxy.address)

        # Should have selected multiple different proxies
        assert len(proxies) > 1

    def test_get_next_proxy_round_robin(self):
        """Test round-robin proxy selection"""
        configs = [
            ProxyConfig("192.168.1.1", 8080),
            ProxyConfig("192.168.1.2", 8080),
            ProxyConfig("192.168.1.3", 8080),
        ]

        manager = ProxyManager(proxy_configs=configs, rotation_strategy="round_robin")

        # Should cycle through proxies in order
        first = manager.get_next_proxy()
        second = manager.get_next_proxy()
        third = manager.get_next_proxy()
        fourth = manager.get_next_proxy()

        assert first.address == "192.168.1.1"
        assert second.address == "192.168.1.2"
        assert third.address == "192.168.1.3"
        assert fourth.address == "192.168.1.1"  # Back to first

    def test_get_next_proxy_least_used(self):
        """Test least-used proxy selection"""
        configs = [
            ProxyConfig("192.168.1.1", 8080),
            ProxyConfig("192.168.1.2", 8080),
            ProxyConfig("192.168.1.3", 8080),
        ]

        manager = ProxyManager(proxy_configs=configs, rotation_strategy="least_used")

        # Use first proxy
        first = manager.get_next_proxy()
        first.last_used = time.time()

        # Use second proxy
        second = manager.get_next_proxy()
        second.last_used = time.time()

        # Third proxy should be selected next (least recently used)
        third = manager.get_next_proxy()
        assert third.address == "192.168.1.3"

    def test_get_next_proxy_no_active(self):
        """Test getting next proxy when none are active"""
        configs = [ProxyConfig("192.168.1.1", 8080), ProxyConfig("192.168.1.2", 8080)]

        manager = ProxyManager(proxy_configs=configs)

        # Deactivate all proxies
        for config in configs:
            config.is_active = False

        proxy = manager.get_next_proxy()
        assert proxy is None

    def test_mark_proxy_failed(self):
        """Test marking proxy as failed"""
        config = ProxyConfig("192.168.1.1", 8080)
        manager = ProxyManager(proxy_configs=[config], max_failures=2)

        # Mark first failure
        manager.mark_proxy_failed(config, "Connection timeout")
        assert config.fail_count == 1
        assert config.is_active is True

        # Mark second failure
        manager.mark_proxy_failed(config, "Connection timeout")
        assert config.fail_count == 2
        assert config.is_active is False  # Should be deactivated

    def test_mark_proxy_success(self):
        """Test marking proxy as successful"""
        config = ProxyConfig("192.168.1.1", 8080)
        config.fail_count = 2

        manager = ProxyManager(proxy_configs=[config])

        manager.mark_proxy_success(config)
        assert config.fail_count == 0

    def test_reactivate_proxies(self):
        """Test reactivating proxies after cooldown"""
        config = ProxyConfig("192.168.1.1", 8080)
        config.is_active = False
        config.fail_count = 3
        config.last_fail_time = time.time() - 400  # 400 seconds ago

        manager = ProxyManager(proxy_configs=[config], failure_cooldown=300)

        manager.reactivate_proxies()
        assert config.is_active is True
        assert config.fail_count == 0

    def test_reactivate_proxies_not_ready(self):
        """Test reactivating proxies before cooldown is complete"""
        config = ProxyConfig("192.168.1.1", 8080)
        config.is_active = False
        config.fail_count = 3
        config.last_fail_time = time.time() - 100  # 100 seconds ago

        manager = ProxyManager(proxy_configs=[config], failure_cooldown=300)

        manager.reactivate_proxies()
        assert config.is_active is False  # Should not be reactivated yet

    @patch("requests.Session")
    def test_health_check_all_success(self, mock_session):
        """Test health check with successful responses"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_session.return_value.get.return_value = mock_response

        configs = [ProxyConfig("192.168.1.1", 8080), ProxyConfig("192.168.1.2", 8080)]

        manager = ProxyManager(proxy_configs=configs)
        results = manager.health_check_all()

        assert len(results) == 2
        assert all(results.values())  # All should be healthy

    @patch("requests.Session")
    def test_health_check_all_mixed(self, mock_session):
        """Test health check with mixed results"""
        # Mock mixed responses
        mock_session.return_value.get.side_effect = [
            MagicMock(status_code=200),  # Success
            Exception("Connection failed"),  # Failure
        ]

        configs = [ProxyConfig("192.168.1.1", 8080), ProxyConfig("192.168.1.2", 8080)]

        manager = ProxyManager(proxy_configs=configs)
        results = manager.health_check_all()

        assert len(results) == 2
        assert results["http://192.168.1.1:8080"] is True
        assert results["http://192.168.1.2:8080"] is False

    def test_get_stats(self):
        """Test getting proxy statistics"""
        configs = [ProxyConfig("192.168.1.1", 8080), ProxyConfig("192.168.1.2", 8080)]

        # Mark one proxy as failed
        configs[0].fail_count = 2
        configs[0].is_active = False

        manager = ProxyManager(proxy_configs=configs, rotation_strategy="round_robin")
        stats = manager.get_stats()

        assert stats["total_proxies"] == 2
        assert stats["active_proxies"] == 1
        assert stats["inactive_proxies"] == 1
        assert stats["total_failures"] == 2
        assert stats["rotation_strategy"] == "round_robin"

    def test_len_and_bool(self):
        """Test length and boolean operations"""
        configs = [ProxyConfig("192.168.1.1", 8080), ProxyConfig("192.168.1.2", 8080)]

        manager = ProxyManager(proxy_configs=configs)

        assert len(manager) == 2
        assert bool(manager) is True

        empty_manager = ProxyManager()
        assert len(empty_manager) == 0
        assert bool(empty_manager) is False


class TestProxyManagerIntegration:
    """Integration tests for ProxyManager"""

    def test_proxy_rotation_with_delays(self):
        """Test proxy rotation respects delays between requests"""
        configs = [ProxyConfig("192.168.1.1", 8080), ProxyConfig("192.168.1.2", 8080)]

        manager = ProxyManager(proxy_configs=configs, min_delay_between_requests=1.0)

        # Get first proxy
        first = manager.get_next_proxy()
        first_time = first.last_used

        # Get second proxy immediately (should be different due to delay)
        second = manager.get_next_proxy()
        second_time = second.last_used

        # Should be different proxies due to delay
        assert first.address != second.address

        # Wait for delay to pass
        time.sleep(1.1)
        third = manager.get_next_proxy()

        # Should be able to reuse first proxy after delay
        assert third.last_used >= first_time + 1.0

    def test_proxy_failover_scenario(self):
        """Test complete proxy failover scenario"""
        configs = [
            ProxyConfig("192.168.1.1", 8080),
            ProxyConfig("192.168.1.2", 8080),
            ProxyConfig("192.168.1.3", 8080),
        ]

        manager = ProxyManager(
            proxy_configs=configs,
            max_failures=2,
            failure_cooldown=1.0,  # Short cooldown for testing
        )

        # Initially all proxies should be active
        assert manager.get_stats()["active_proxies"] == 3

        # Fail first proxy twice
        manager.mark_proxy_failed(configs[0], "Error 1")
        manager.mark_proxy_failed(configs[0], "Error 2")

        # First proxy should be deactivated
        assert not configs[0].is_active
        assert manager.get_stats()["active_proxies"] == 2

        # Fail second proxy twice
        manager.mark_proxy_failed(configs[1], "Error 1")
        manager.mark_proxy_failed(configs[1], "Error 2")

        # Second proxy should be deactivated
        assert not configs[1].is_active
        assert manager.get_stats()["active_proxies"] == 1

        # Only third proxy should be available
        proxy = manager.get_next_proxy()
        assert proxy.address == "192.168.1.3"

        # Wait for cooldown and reactivate
        time.sleep(1.1)
        manager.reactivate_proxies()

        # All proxies should be active again
        assert manager.get_stats()["active_proxies"] == 3
