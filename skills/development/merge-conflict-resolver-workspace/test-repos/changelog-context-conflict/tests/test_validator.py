from src.utils.validator import validate_range

def test_validate_range():
    assert validate_range(5, 0, 10) == True
    assert validate_range(0, 0, 10) == True
    assert validate_range(10, 0, 10) == True  # This will fail with the bug
