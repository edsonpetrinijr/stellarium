from Variables import RADIUS
import math


def rotate_point(x, y, z, lat, lon):
    """
    Rotaciona um ponto (x, y, z) em uma esfera:
    - primeiro uma rotação pela longitude (em torno do eixo z),
    - depois uma rotação pela latitude (em torno do eixo x).
    
    lat e lon são em radianos.
    """
    # Rotação em torno do eixo Z (longitude)
    x1 = x * math.cos(lon) - y * math.sin(lon)
    y1 = x * math.sin(lon) + y * math.cos(lon)
    z1 = z
    lat -= math.pi/2
    # Rotação em torno do eixo X (latitude)
    x2 = x1
    y2 = y1 * math.cos(lat) - z1 * math.sin(lat)
    z2 = y1 * math.sin(lat) + z1 * math.cos(lat)

    # Convertendo de volta para coordenadas esféricas (opcional)
    r = math.sqrt(x2**2 + y2**2 + z2**2)
    theta_new = math.acos(z2 / r)  # ângulo zenital
    phi_new = math.atan2(y2, x2)   # ângulo azimutal (longitude)

    return x2, y2, z2, theta_new, phi_new