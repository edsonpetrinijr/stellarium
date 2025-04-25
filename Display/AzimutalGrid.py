from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy as np

import math

from Variables import *

def draw_sphere_grid(lat_segments=36, lon_segments=36):

    glPushMatrix()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.7, 1.0, 0.7, 0.3)

    for i in range(1, lat_segments):
        lat_angle = math.pi * i / lat_segments
        glBegin(GL_LINE_LOOP)
        for j in range(lon_segments + 1):
            lon_angle = 2 * math.pi * j / lon_segments
            x = RADIUS * math.sin(lat_angle) * math.cos(lon_angle)
            y = RADIUS * math.sin(lat_angle) * math.sin(lon_angle)
            z = RADIUS * math.cos(lat_angle)
            glVertex3f(x, y, z)
        glEnd()

    for j in range(lon_segments):
        lon_angle = 2 * math.pi * j / lon_segments
        glBegin(GL_LINE_STRIP)
        for i in range(lat_segments + 1):
            lat_angle = math.pi * i / lat_segments
            x = RADIUS * math.sin(lat_angle) * math.cos(lon_angle)
            y = RADIUS * math.sin(lat_angle) * math.sin(lon_angle)
            z = RADIUS * math.cos(lat_angle)
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

def draw_morphing_upper_sphere_grid(
    t,
    lat_segments=18,
    lon_segments=24,
    resolution=3,
    projection_type="ayre_expanded"
):
    # choose projection function
    if projection_type == "orthographic":
        proj = orthographic_projection
    elif projection_type == "ayre":
        proj = ayre_projection
    elif projection_type == "ayre_expanded":
        proj = ayre_expanded_projection
    elif projection_type == "stereographic":
        proj = stereographic_projection
    else:
        raise ValueError(f"Unknown projection: {projection_type}")

    lon_samples = lon_segments * resolution
    lat_samples = lat_segments * resolution
    half = lat_segments // 2

    glPushMatrix()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # LOWER HEMISPHERE (fade out)
    base_alpha = 0.3
    lower_alpha = base_alpha * (1.0 - t)
    glColor4f(0.7, 1.0, 0.7, lower_alpha)
    if t < 0.75:
        for i in range(1, half):
            phi = math.pi * i / lat_segments
            z0 = -RADIUS * math.cos(phi)
            glBegin(GL_LINE_LOOP)
            for j in range(lon_samples):
                theta = 2 * math.pi * j / lon_samples
                x = RADIUS * math.sin(phi) * math.cos(theta)
                y = RADIUS * math.sin(phi) * math.sin(theta)
                glVertex3f(x, y, z0)
            glEnd()
        for j in range(lon_segments):
            theta = 2 * math.pi * j / lon_segments
            glBegin(GL_LINE_STRIP)
            for k in range(lat_samples // 2 + 1):
                phi = math.pi * k / lat_samples
                x = RADIUS * math.sin(phi) * math.cos(theta)
                y = RADIUS * math.sin(phi) * math.sin(theta)
                z0 = -RADIUS * math.cos(phi)
                glVertex3f(x, y, z0)
            glEnd()

    # UPPER HEMISPHERE MORPH USING LINEAR INTERPOLATION
    base_alpha = 0.3
    glColor4f(0.7, 1.0, 0.7, base_alpha)
    z_end = 100.0  # projection plane height

    def _lerp(p0, p1, u):
        return tuple((1 - u) * a + u * b for a, b in zip(p0, p1))

    for i in range(half + 1):
        phi = math.pi * i / lat_segments
        z_s = RADIUS * math.cos(phi)
        glBegin(GL_LINE_LOOP)
        for j in range(lon_samples):
            theta = 2 * math.pi * j / lon_samples
            x = RADIUS * math.sin(phi) * math.cos(theta)
            y = RADIUS * math.sin(phi) * math.sin(theta)
            nx, ny = proj(x, y, z_s, t)
            p0 = (x, y, z_s)
            p1 = (nx, ny, z_end)
            xp, yp, zp = _lerp(p0, p1, t)
            glVertex3f(xp, yp, zp)
        glEnd()
    for j in range(lon_segments):
        theta = 2 * math.pi * j / lon_segments
        glBegin(GL_LINE_STRIP)
        for k in range(lat_samples // 2 + 1):
            phi = math.pi * k / lat_samples
            x = RADIUS * math.sin(phi) * math.cos(theta)
            y = RADIUS * math.sin(phi) * math.sin(theta)
            z_s = RADIUS * math.cos(phi)
            nx, ny = proj(x, y, z_s, t)
            p0 = (x, y, z_s)
            p1 = (nx, ny, z_end)
            xp, yp, zp = _lerp(p0, p1, t)
            glVertex3f(xp, yp, zp)
        glEnd()

    glPopMatrix()


def draw_morphing_upper_sphere_grid_copy(
    t,
    lat_segments=18,
    lon_segments=24,
    resolution=3,
    projection_type="ayre_expanded"
):
    # choose projection function
    if projection_type == "orthographic":
        proj = orthographic_projection
    elif projection_type == "ayre":
        proj = ayre_projection
    elif projection_type == "ayre_expanded":
        proj = ayre_expanded_projection
    elif projection_type == "stereographic":
        proj = stereographic_projection
    else:
        raise ValueError(f"Unknown projection: {projection_type}")

    lon_samples = lon_segments * resolution
    lat_samples = lat_segments * resolution
    half = lat_segments // 2

    glPushMatrix()
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # LOWER HEMISPHERE (fade out)
    base_alpha = 0.3
    lower_alpha = base_alpha * (1.0 - t)
    glColor4f(0.7, 1.0, 0.7, lower_alpha)
    # draw lower hemisphere:
    for i in range(1, half):
        phi = math.pi * i / lat_segments
        z0 = -RADIUS * math.cos(phi)
        glBegin(GL_LINE_LOOP)
        for j in range(lon_samples):
            theta = 2 * math.pi * j / lon_samples
            x = RADIUS * math.sin(phi) * math.cos(theta)
            y = RADIUS * math.sin(phi) * math.sin(theta)
            glVertex3f(x, y, z0)
        glEnd()
    for j in range(lon_segments):
        theta = 2 * math.pi * j / lon_segments
        glBegin(GL_LINE_STRIP)
        for k in range(lat_samples // 2 + 1):
            phi = math.pi * k / lat_samples
            x = RADIUS * math.sin(phi) * math.cos(theta)
            y = RADIUS * math.sin(phi) * math.sin(theta)
            z0 = -RADIUS * math.cos(phi)
            glVertex3f(x, y, z0)
        glEnd()

    # UPPER HEMISPHERE MORPH WITH CIRCULAR ARC AROUND (0,0,z_end)
    base_alpha = 0.3
    glColor4f(0.7, 1.0, 0.7, base_alpha)
    z_end = 100.0  # projection plane height
    center = (0.0, 0.0, z_end)

    def _circle_arc(p0, p1, center, u):
        # rotate p0->p1 about center on a circle of radius |p0-center|
        x0, y0, z0 = p0
        x1, y1, _ = p1  # ignore z of p1, will recompute radius
        cx, cy, cz = center
        # vectors from center
        v0 = (x0 - cx, y0 - cy, z0 - cz)
        R = math.sqrt(sum(c*c for c in v0))
        # project p1 onto sphere radius R
        v1_dir = (x1 - cx, y1 - cy, 0.0)
        d1 = math.hypot(v1_dir[0], v1_dir[1])
        if R < 1e-6 or d1 < 1e-6:
            return (x0, y0, z0)
        v1 = (v1_dir[0]*(R/d1), v1_dir[1]*(R/d1), 0.0)
        # angle between v0 and v1 in plane z=z_end
        dot = v0[0]*v1[0] + v0[1]*v1[1] + v0[2]*v1[2]
        cos_ang = max(-1.0, min(1.0, dot/(R*R)))
        ang = math.acos(cos_ang)
        # axis is perpendicular to plane containing v0, v1
        ax, ay, az = v0[1]*v1[2] - v0[2]*v1[1],v0[2]*v1[0] - v0[0]*v1[2],v0[0]*v1[1] - v0[1]*v1[0]
        norm = math.sqrt(ax*ax + ay*ay + az*az)
        if norm < 1e-6:
            return (x0, y0, z0)
        ax, ay, az = ax/norm, ay/norm, az/norm
        cos_t = math.cos(ang*u)
        sin_t = math.sin(ang*u)
        # Rodrigues' formula: rotate v0
        dot_av0 = ax*v0[0] + ay*v0[1] + az*v0[2]
        cross = (ay*v0[2] - az*v0[1], az*v0[0] - ax*v0[2], ax*v0[1] - ay*v0[0])
        v_rot = (
            v0[0]*cos_t + cross[0]*sin_t + ax*dot_av0*(1-cos_t),
            v0[1]*cos_t + cross[1]*sin_t + ay*dot_av0*(1-cos_t),
            v0[2]*cos_t + cross[2]*sin_t + az*dot_av0*(1-cos_t),
        )
        return (cx + v_rot[0], cy + v_rot[1], cz + v_rot[2])

    # draw upper hemisphere
    for i in range(half+1):
        phi = math.pi * i / lat_segments
        z_s = RADIUS * math.cos(phi)
        glBegin(GL_LINE_LOOP)
        for j in range(lon_samples):
            theta = 2 * math.pi * j / lon_samples
            x = RADIUS * math.sin(phi) * math.cos(theta)
            y = RADIUS * math.sin(phi) * math.sin(theta)
            # compute projected XY
            nx, ny = proj(x, y, z_s, t)
            p0 = (x, y, z_s)
            p1 = (nx, ny, z_end)
            xp, yp, zp = _circle_arc(p0, p1, center, t)
            glVertex3f(xp, yp, zp)
        glEnd()
    for j in range(lon_segments):
        theta = 2 * math.pi * j / lon_segments
        glBegin(GL_LINE_STRIP)
        for k in range(lat_samples//2 + 1):
            phi = math.pi * k / lat_samples
            x = RADIUS * math.sin(phi) * math.cos(theta)
            y = RADIUS * math.sin(phi) * math.sin(theta)
            z_s = RADIUS * math.cos(phi)
            nx, ny = proj(x, y, z_s, t)
            p0 = (x, y, z_s)
            p1 = (nx, ny, z_end)
            xp, yp, zp = _circle_arc(p0, p1, center, t)
            glVertex3f(xp, yp, zp)
        glEnd()

    glPopMatrix()
