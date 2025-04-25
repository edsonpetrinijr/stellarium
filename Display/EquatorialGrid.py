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
