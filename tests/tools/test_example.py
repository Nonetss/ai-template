from tools.example.tools import get_current_time


def test_get_current_time_returns_iso_string():
    result = get_current_time()
    assert "T" in result  # ISO 8601 format
    assert result.endswith("+00:00")
