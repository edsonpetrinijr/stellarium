from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math

from Variables import *

def draw_equatorial_sphere_grid(lat, lat_segments=18, lon_segments=24):
    glPushMatrix()

    # Rotação da latitude aplicada no eixo Y (agora o eixo Z é o vertical da esfera)
    glRotatef(math.degrees(lat-math.pi/2), 1.0, 0.0, 0.0)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.7, 0.7, 1.0, 0.3)

    for i in range(1, lat_segments):
        lat_angle = math.pi * i / lat_segments
        glBegin(GL_LINE_LOOP)
        for j in range(lon_segments + 1):
            lon_angle = 2 * math.pi * j / lon_segments
            x = RADIUS * math.sin(lat_angle) * math.cos(lon_angle)
            z = RADIUS * math.cos(lat_angle)
            y = RADIUS * math.sin(lat_angle) * math.sin(lon_angle)
            glVertex3f(x, y, z)
        glEnd()

    for j in range(lon_segments):
        lon_angle = 2 * math.pi * j / lon_segments
        glBegin(GL_LINE_STRIP)
        for i in range(lat_segments + 1):
            lat_angle = math.pi * i / lat_segments
            x = RADIUS * math.sin(lat_angle) * math.cos(lon_angle)
            z = RADIUS * math.cos(lat_angle)
            y = RADIUS * math.sin(lat_angle) * math.sin(lon_angle)
            glVertex3f(x, y, z)
        glEnd()

    glPopMatrix()
    
def orthographic_projection(x, y, z, t):
    return x, y  # No change to the x, y coordinates

def stereographic_projection(x, y, z, t):
    ponto = np.array([x, y, z])
    r = np.linalg.norm(ponto)
    theta_new = math.acos(z / r)
    phi_new = math.atan2(y, x)
    return 2 * RADIUS * math.tan(theta_new/2) * math.cos(phi_new), 2*RADIUS * math.tan(theta_new/2) * math.sin(phi_new)

def ayre_projection(x, y, z, t):
    ponto = np.array([x, y, z])
    r = np.linalg.norm(ponto)
    theta_new = math.acos(z / r)
    factor = (2 * theta_new) / math.pi
    phi_new = math.atan2(y, x)
    return factor * math.cos(phi_new)*RADIUS, factor * math.sin(phi_new)*RADIUS

def ayre_expanded_projection(x, y, z, t):
    ponto = np.array([x, y, z])
    r = np.linalg.norm(ponto)
    theta_new = math.acos(z / r)
    phi_new = math.atan2(y, x)
    return theta_new * math.cos(phi_new)*RADIUS, theta_new * math.sin(phi_new)*RADIUS

def perspective_projection(x, y, z, t, d=500):
    factor = d / (d - z)  # Simulating a perspective with a distance `d`
    return x * factor, y * factor



def draw_morphing_equatorial_sphere_grid(
    lat,                       # the “tilt” of the equator (in radians)
    t,                         # morph factor in [0,1]
    lat_segments=18,
    lon_segments=24,
    resolution=4,
    projection_type="ayre_expanded",
    z_plane=100.0
):
    # base transparency
    base_alpha = 0.3

    # Select projection function
    if projection_type == "orthographic":
        proj = orthographic_projection
    elif projection_type == "ayre":
        proj = ayre_projection
    elif projection_type == "ayre_expanded":
        proj = ayre_expanded_projection
    elif projection_type == "stereographic":
        proj = stereographic_projection
    elif projection_type == "perspective":
        proj = lambda x, y, z, t: perspective_projection(x, y, z, t)
    else:
        raise ValueError(f"Unknown projection: {projection_type}")

    # Precompute rotation about the X-axis by (lat - pi/2)
    alpha = lat - math.pi/2
    cos_a = math.cos(alpha)
    sin_a = math.sin(alpha)

    def _rotate(x, y, z):
        x_r = x
        y_r = y * cos_a - z * sin_a
        z_r = y * sin_a + z * cos_a
        return x_r, y_r, z_r

    def _lerp(p0, p1, u):
        return tuple((1-u)*a + u*b for a, b in zip(p0, p1))

    # Sampling density
    lon_samples = lon_segments * resolution
    lat_samples = lat_segments * resolution

    # GL setup with line smoothing
    glPushMatrix()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

    # t==0: full grid always visible
    if t <= 0:
        glColor4f(0.7, 0.7, 1.0, base_alpha)
        # latitude rings
        for i in range(1, lat_segments):
            phi = math.pi * i / lat_segments
            glBegin(GL_LINE_LOOP)
            for j in range(lon_samples + 1):
                theta = 2 * math.pi * j / lon_samples
                x = RADIUS * math.sin(phi) * math.cos(theta)
                y = RADIUS * math.sin(phi) * math.sin(theta)
                z = RADIUS * math.cos(phi)
                xr, yr, zr = _rotate(x, y, z)
                glVertex3f(xr, yr, zr)
            glEnd()
        # longitude meridians
        for j in range(lon_segments):
            theta = 2 * math.pi * j / lon_segments
            glBegin(GL_LINE_STRIP)
            for i in range(lat_samples + 1):
                phi = math.pi * i / lat_samples
                x = RADIUS * math.sin(phi) * math.cos(theta)
                y = RADIUS * math.sin(phi) * math.sin(theta)
                z = RADIUS * math.cos(phi)
                xr, yr, zr = _rotate(x, y, z)
                glVertex3f(xr, yr, zr)
            glEnd()
        glPopMatrix()
        return

    # Helper: draw segments with per-flag transparency
    def _draw_segments(samples):
        # samples: list of (x,y,z,above_flag)
        start = 0
        flag = samples[0][3]
        for idx in range(1, len(samples)):
            if samples[idx][3] != flag:
                # draw segment from start to idx-1
                if idx - start >= 2:
                    # choose appropriate alpha
                    alpha_seg = base_alpha if flag else base_alpha * (1 - t)
                    glColor4f(0.7, 0.7, 1.0, alpha_seg)
                    glBegin(GL_LINE_STRIP)
                    for k in range(start, idx):
                        xk, yk, zk, _ = samples[k]
                        if not(t>0.98 and zk<0):
                            glVertex3f(xk, yk, zk)
                    glEnd()
                start = idx
                flag = samples[idx][3]
        # final segment
        if len(samples) - start >= 2:
            alpha_seg = base_alpha if flag else base_alpha * (1 - t)
            glColor4f(0.7, 0.7, 1.0, alpha_seg)
            glBegin(GL_LINE_STRIP)
            for k in range(start, len(samples)):
                xk, yk, zk, _ = samples[k]
                if not(t>0.98 and zk<0):
                    glVertex3f(xk, yk, zk)
            glEnd()

    # Draw rings, splitting at z=0 boundary
    for i in range(1, lat_segments):
        phi = math.pi * i / lat_segments
        samples = []
        for j in range(lon_samples + 1):
            theta = 2 * math.pi * j / lon_samples
            x = RADIUS * math.sin(phi) * math.cos(theta)
            y = RADIUS * math.sin(phi) * math.sin(theta)
            z = RADIUS * math.cos(phi)
            xr, yr, zr = _rotate(x, y, z)
            if zr > 0:
                nx, ny = proj(xr, yr, zr, t)
                xp, yp, zp = _lerp((xr, yr, zr), (nx, ny, z_plane), t)
                above = True
            else:
                xp, yp, zp = xr, yr, zr
                above = False
            samples.append((xp, yp, zp, above))
        _draw_segments(samples)

    # Draw meridians, splitting at z=0 boundary
    for j in range(lon_segments):
        theta = 2 * math.pi * j / lon_segments
        samples = []
        for i in range(lat_samples + 1):
            phi = math.pi * i / lat_samples
            x = RADIUS * math.sin(phi) * math.cos(theta)
            y = RADIUS * math.sin(phi) * math.sin(theta)
            z = RADIUS * math.cos(phi)
            xr, yr, zr = _rotate(x, y, z)
            if zr > 0:
                nx, ny = proj(xr, yr, zr, t)
                xp, yp, zp = _lerp((xr, yr, zr), (nx, ny, z_plane), t)
                above = True
            else:
                xp, yp, zp = xr, yr, zr
                above = False
            samples.append((xp, yp, zp, above))
        _draw_segments(samples)

    glPopMatrix()

