from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math

from Variables import *
from utils.conversions import *

from main import *


def draw_visible_sphere(radius=101.0):
    glColor4f(0.2, 0.3, 0.5, 0.1)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_FILL)
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluSphere(quadric, radius, 40, 40)
    gluDeleteQuadric(quadric)
    glDisable(GL_BLEND)

def draw_sphere_grid(radius=100.0, lat_segments=36, lon_segments=36):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.7, 0.7, 1.0, 0.3)
    for i in range(1, lat_segments):
        lat = math.pi * i / lat_segments
        glBegin(GL_LINE_LOOP)
        for j in range(lon_segments + 1):
            lon = 2 * math.pi * j / lon_segments
            x = radius * math.sin(lat) * math.cos(lon)
            y = radius * math.cos(lat)
            z = radius * math.sin(lat) * math.sin(lon)
            glVertex3f(x, y, z)
        glEnd()

    for j in range(lon_segments):
        lon = 2 * math.pi * j / lon_segments
        glBegin(GL_LINE_STRIP)
        for i in range(lat_segments + 1):
            lat = math.pi * i / lat_segments
            x = radius * math.sin(lat) * math.cos(lon)
            y = radius * math.cos(lat)
            z = radius * math.sin(lat) * math.sin(lon)
            glVertex3f(x, y, z)
        glEnd()
