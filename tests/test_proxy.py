"""Tests for ProxyManager in patchtroy."""

from pathlib import Path

from patchtroy.proxy import ProxyItem, ProxyManager


def test_proxy_item_quarantine():
    item = ProxyItem(server="http://proxy1.test:8080")
    assert item.is_healthy is True

    # Mark 2 failures (threshold 3)
    item.mark_failure(max_failures=3, quarantine_seconds=10.0)
    item.mark_failure(max_failures=3, quarantine_seconds=10.0)
    assert item.is_healthy is True

    # 3rd failure quarantines
    item.mark_failure(max_failures=3, quarantine_seconds=10.0)
    assert item.is_healthy is False

    # Success clears
    item.mark_success()
    assert item.is_healthy is True
    assert item.failures == 0


def test_proxy_manager_round_robin():
    proxies = ["http://1.1.1.1:8080", "http://2.2.2.2:8080", "http://3.3.3.3:8080"]
    pm = ProxyManager(proxies=proxies, strategy="round-robin")
    assert len(pm) == 3

    assert pm.get_proxy() == "http://1.1.1.1:8080"
    assert pm.get_proxy() == "http://2.2.2.2:8080"
    assert pm.get_proxy() == "http://3.3.3.3:8080"
    assert pm.get_proxy() == "http://1.1.1.1:8080"


def test_proxy_manager_random():
    proxies = ["http://1.1.1.1:8080", "http://2.2.2.2:8080"]
    pm = ProxyManager(proxies=proxies, strategy="random")
    selected = {pm.get_proxy() for _ in range(20)}
    assert selected.issubset(set(proxies))


def test_proxy_manager_from_file(tmp_path: Path):
    proxy_file = tmp_path / "proxies.txt"
    proxy_file.write_text("# Comment\nhttp://10.0.0.1:8000\n\n10.0.0.2:8000\n", encoding="utf-8")

    pm = ProxyManager(proxies=proxy_file)
    assert len(pm) == 2
    assert pm.get_proxy() == "http://10.0.0.1:8000"
    assert pm.get_proxy() == "http://10.0.0.2:8000"


def test_proxy_manager_quarantine_fallback():
    proxies = ["http://p1.test:8000", "http://p2.test:8000"]
    pm = ProxyManager(proxies=proxies, max_failures=1, quarantine_seconds=5.0)

    # Quarantine p1
    pm.report_failure("http://p1.test:8000")

    # Next calls should exclusively return p2
    assert pm.get_proxy() == "http://p2.test:8000"
    assert pm.get_proxy() == "http://p2.test:8000"

    # Quarantine p2 as well -> both quarantined, fallback should still return a proxy without crash
    pm.report_failure("http://p2.test:8000")
    fallback = pm.get_proxy()
    assert fallback in proxies
