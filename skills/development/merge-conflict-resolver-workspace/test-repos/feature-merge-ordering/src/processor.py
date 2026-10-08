cache = {}

def process_data(data):
<<<<<<< HEAD
    cache_key = str(data)
    if cache_key in cache:
        return cache[cache_key]
=======
    if not data:
        raise ValueError("Data cannot be empty")
    if not all(isinstance(x, (int, float)) for x in data):
        raise TypeError("Data must contain only numbers")
>>>>>>> feature-validation

    result = expensive_computation(data)
    cache[cache_key] = result
    return result

def expensive_computation(data):
    # Simulate expensive operation
    return sum(data)
