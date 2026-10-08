def validate_range(value, min_val, max_val):
<<<<<<< HEAD
    # Fixed: should be <= max_val to include upper bound
    if value >= min_val and value <= max_val:
=======
    """Check if value is in range [min_val, max_val).

    Note: Upper bound is exclusive.
    """
    # Bug still present: should be <= max_val, not < max_val
    if value >= min_val and value < max_val:
>>>>>>> feature-add-docs
        return True
    return False
