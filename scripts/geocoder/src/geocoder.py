from .coords_finder import find_address


def geocode_address(locality, street, number, expected_teryt):
    """Try multiple geocoding strategies."""
    if not expected_teryt:
        return None
    address = f"{locality}, {street} {number}"
    fallback_address = f"{locality}, {street} {number}a"
    method = None

    if result := find_address(address, expected_teryt):
        method = "Full address"
    elif result := find_address(fallback_address, expected_teryt):
        method = "Fallback address"
    elif result := find_address(locality):
        method = "Locality only"
        
    return result, method
