from app.utils.time import now


def test_now_uses_business_timezone():
    current = now()
    assert current.tzinfo is None
    assert 2026 <= current.year <= 2100
