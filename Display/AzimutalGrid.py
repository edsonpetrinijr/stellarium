from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

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
            y = RADIUS * math.cos(lat_angle)
            z = RADIUS * math.sin(lat_angle) * math.sin(lon_angle)
            glVertex3f(x, y, z)
        glEnd()

    for j in range(lon_segments):
        lon_angle = 2 * math.pi * j / lon_segments
        glBegin(GL_LINE_STRIP)
        for i in range(lat_segments + 1):
            lat_angle = math.pi * i / lat_segments
            x = RADIUS * math.sin(lat_angle) * math.cos(lon_angle)
            y = RADIUS * math.cos(lat_angle)
            z = RADIUS * math.sin(lat_angle) * math.sin(lon_angle)
            glVertex3f(x, y, z)
        glEnd()

    glPopMatrix()
