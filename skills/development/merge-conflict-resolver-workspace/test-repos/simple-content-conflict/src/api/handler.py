import logging

def process_request(data):
<<<<<<< HEAD
    try:
        result = transform_data(data)
        return result
    except Exception as e:
        return {"error": str(e)}
=======
    logging.info(f"Processing request with data: {data}")
    result = transform_data(data)
    logging.info(f"Request processed successfully")
    return result
>>>>>>> feature-logging

def transform_data(data):
    return data.upper()
