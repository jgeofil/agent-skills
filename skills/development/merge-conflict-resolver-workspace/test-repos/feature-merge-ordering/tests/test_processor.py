from src.processor import process_data

def test_process_data():
    assert process_data([1, 2, 3]) == 6
