import pytest

from autoflow.headless_browser import HeadlessBrowser


def test_headless_browser_normalizes_plain_hosts_and_rejects_unsafe_schemes():
    assert HeadlessBrowser._normalize_url("example.com/search?q=autoflow") == "https://example.com/search?q=autoflow"
    assert HeadlessBrowser._normalize_url("http://127.0.0.1:8765/") == "http://127.0.0.1:8765/"

    with pytest.raises(ValueError, match="http 或 https"):
        HeadlessBrowser._normalize_url("file:///C:/private.txt")
    with pytest.raises(ValueError, match="http 或 https"):
        HeadlessBrowser._normalize_url("javascript:alert(1)")
