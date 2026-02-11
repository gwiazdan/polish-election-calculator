from .coords_finder import find_address


def geocode_address(locality, street, number, expected_teryt):
    """Try multiple geocoding strategies."""
    if not expected_teryt:
        return None
    address = f"{locality}, {street} {number}"
    fallback_address = f"{locality}, {street} {number}a"
    return find_address(address, expected_teryt) or find_address(
        fallback_address, expected_teryt
    )
