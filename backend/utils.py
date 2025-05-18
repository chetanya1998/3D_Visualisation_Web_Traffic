def get_cube_id_from_ip(ip: str) -> int:
    """
    Extracts the cube ID from the last octet of an IP address.
    This helps distribute traffic across 4 cubes.

    Example: IP '203.0.113.25' → 25 % 4 → cube 1
    """
    try:
        last_octet = int(ip.strip().split(".")[-1])
        return last_octet % 4  # 4 cubes → IDs 0 to 3
    except Exception:
        return 0  # default cube
