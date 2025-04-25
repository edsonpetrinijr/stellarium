from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from Variables import *

def draw_ground(grid_step=2.5, z=0.0):
    glColor4f(0.65, 0.45, 0.25, 0.75)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Linhas paralelas ao eixo X (horizontal), dentro do círculo
    y = -RADIUS
    while y <= RADIUS:
        max_x = (RADIUS**2 - y**2)**0.5  # limite do X para esse Y (círculo)
        glBegin(GL_LINES)
        glVertex3f(-max_x, y, z)
        glVertex3f(max_x, y, z)
        glEnd()
        y += grid_step

    # Linhas paralelas ao eixo Y (vertical), dentro do círculo
    x = -RADIUS
    while x <= RADIUS:
        max_y = (RADIUS**2 - x**2)**0.5  # limite do Y para esse X (círculo)
        glBegin(GL_LINES)
        glVertex3f(x, -max_y, z)
        glVertex3f(x, max_y, z)
        glEnd()
        x += grid_step

    glDisable(GL_BLEND)
