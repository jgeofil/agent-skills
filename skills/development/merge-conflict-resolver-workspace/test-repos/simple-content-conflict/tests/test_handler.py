from src.api.handler import process_request, transform_data

def test_transform_data():
    assert transform_data("hello") == "HELLO"
