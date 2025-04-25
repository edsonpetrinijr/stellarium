def lerp_angle(start, end, t):
    diff = (end - start + 180) % 360 - 180
    return (start + diff * t) % 360