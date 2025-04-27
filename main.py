import copy
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image

import math
import pandas as pd
import numpy as np

from Display.CelestialSphere import *
from Display.Ground import *
from Variables import *
# from video.save_video import *
from Display.Stars import *
from Display.EquatorialGrid import *
from Display.AzimutalGrid import *

from utils.conversions import *

import threading

def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_POINT_SMOOTH)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
    generate_points_on_sphere()
    
    #Edson veja: Heitor
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_ALPHA_TEST)


def display():
    global RADIUS, t, desenhar_chao, desenhar_grade_equatorial,desenhar_grade_azimutal, lat, lon, estrelas_carta_celeste, estrelas_esfera_celeste, go_to_star, camera_normal
    global camera_carta_celeste, camera_lateral, t
    global projection_type
    glClearColor(red, green, blue, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    lx = math.cos(math.radians(pitch)) * math.sin(math.radians(yaw))
    ly = -math.cos(math.radians(pitch)) * math.cos(math.radians(yaw))
    lz = viewer_height + math.sin(math.radians(pitch))
    # gluLookAt(0, viewer_height, 0, lx, ly, lz, 0, 1, 0)
    gluLookAt(0, 0, viewer_height, lx, ly, lz, 0, 0, 1)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_FRONT)

    
    if (camera_carta_celeste or camera_lateral):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspect = width / height if height != 0 else 1
        size = RADIUS + fov # quanto maior, mais "zoom out"

        glOrtho(-size * aspect, size * aspect, -size, size, -1000, 1000)

        if (camera_carta_celeste):
            gluLookAt(
                0, 0, -90,    # posição do observador (centro da esfera)
                0, 0, 0,    # ponto para onde está olhando (eixo Y positivo)
                0, 1, 0     # vetor 'up' (Z positivo para manter orientação "natural")
            )

        elif (camera_lateral):
            gluLookAt(
                0, -90, 0,    # posição do observador (centro da esfera)
                0, 0, 0,    # ponto para onde está olhando (eixo Y positivo)
                0, 0, 1     # vetor 'up' (Z positivo para manter orientação "natural")
            )
            
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    else:
        update_projection()

    if desenhar_chao:
        draw_ground()
    if desenhar_grade_equatorial:
        #draw_equatorial_sphere_grid(lat)
        if estrelas_carta_celeste:
            target_t = 1
        else:
            target_t = 0
        dt = target_t - t
        t += dt * SPEED
        
        if t < 0.05:
            t = 0
        draw_morphing_equatorial_sphere_grid(lat,t, projection_type=projection_type)
    if desenhar_grade_azimutal:
        if estrelas_carta_celeste:
            target_t = 1
        else:
            target_t = 0
        dt = target_t - t
        t += dt * SPEED
        
        if t < 0.05:
            t = 0
        
        draw_morphing_upper_sphere_grid(t, projection_type=projection_type)

    draw_stars(go_to_star, estrelas_esfera_celeste, estrelas_carta_celeste, star_color, lat, lon)

    glDisable(GL_CULL_FACE)
    glutSwapBuffers()

def update_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = width / height if height != 0 else 1
    # gluPerspective(fov, aspect, 0.1, 200.0)
    gluPerspective(fov, aspect, 0.1, 1000000.0)
    glMatrixMode(GL_MODELVIEW)

def mouse(button, state, x, y):
    global mouse_down, move, last_x, last_y, fov, visao_carta_celeste

    if button == GLUT_LEFT_BUTTON:
        mouse_down = (state == GLUT_DOWN)
        last_x = x
        last_y = y
    elif button == 3:
        zoom_in()
    elif button == 4:
        zoom_out()

def zoom_in():
    global fov
    fov = max(5, fov - 2)
    update_projection()
    glutPostRedisplay()

def zoom_out():
    global fov
    fov = min(120, fov + 2)
    update_projection()
    glutPostRedisplay()
    
def motion(x, y):
    # MUDAR ROLL    
    global mouse_down, move, yaw, pitch, last_x, last_y, fov

    if mouse_down:
        dx = x - last_x
        dy = y - last_y
        yaw += dx * ((fov / 3) * 0.01)   # rotação ao redor do eixo Z
        yaw = yaw % 360
        pitch += dy * ((fov / 3) * 0.01)  # rotação ao redor do eixo Y
        pitch = max(-90, min(90, pitch))

        last_x = x
        last_y = y
        glutPostRedisplay()

def save_screenshot(filename="high_res_screenshot.png"):
    # Obtém o tamanho atual da janela OpenGL
    viewport = glGetIntegerv(GL_VIEWPORT)
    x, y, width, height = viewport

    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(x, y, width, height, GL_RGB, GL_UNSIGNED_BYTE)
    image = Image.frombytes("RGB", (width, height), data)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)

    image.save(filename)
    print(f"Imagem salva como {filename} ({width}x{height})")

def keyboard(key, x, y):
    print(key)
    """
        1, 2, 3: Câmeras
        # I, O, P : Posição Real, Esfera, Plano
        C: Inverter Cor
        # Projeção
        E, Z, G: Grade Equatorial, Azimutal, Chão
    """
    global estrelas_carta_celeste, estrelas_esfera_celeste, desenhar_chao, desenhar_grade_equatorial, desenhar_grade_azimutal, red, green, blue, star_color, viewer_height, go_to_star
    global camera_normal, camera_carta_celeste, camera_lateral
    global t

    if key == b'1':
        camera_carta_celeste = False
        camera_lateral = False
    elif key == b'2':
        camera_carta_celeste = True
        camera_lateral = False
    elif key == b'3':
        camera_carta_celeste = False
        camera_lateral = True

    elif key == b'e':
        desenhar_grade_equatorial = not desenhar_grade_equatorial
    elif key == b'z':
        desenhar_grade_azimutal = not desenhar_grade_azimutal
    elif key == b'g':
        desenhar_chao = not desenhar_chao
    
    elif key == b'i':
        estrelas_esfera_celeste = False
        estrelas_carta_celeste = False
    elif key == b'o':
        estrelas_esfera_celeste = True
        estrelas_carta_celeste = False
    elif key == b'p':
        estrelas_esfera_celeste = False
        estrelas_carta_celeste = True
    
    elif key == b't':
        go_to_star = not go_to_star

    elif key == b'c':
        if (not red == 1):
            red, green, blue = 1, 1, 1
            star_color = (0,0,0)
        else:
            red = 0.05
            green = 0.05
            blue = 0.1
            star_color = (1,1,1)

def specialKeyboard(key, x, y):
    print(key)

    if key == GLUT_KEY_F2:
        save_screenshot()
    elif key == GLUT_KEY_F11:
        glutFullScreenToggle()

def reshape(w, h):
    global width, height
    width, height = w, h

    glViewport(0, 0, width, height)

    update_projection()

def get_new_lon():
    global lon

    while True:
        try:
            new_lon = int(input('Nova longitude (-180 a 180): '))
            if -180 <= new_lon <= 180:
                lon = np.radians(new_lon)
                print(f"Longitude atualizada para: {lon} radianos")
                glutPostRedisplay()  # Solicita o redesenho da tela
            else:
                print("A longitude deve estar entre -180 e 180 graus.")
        except ValueError:
            print("Por favor, insira um número válido.")

def get_new_lat():
    global lat

    while True:
        try:
            new_lat = int(input('Nova latitude (-90 a 90): '))
            if -90 <= new_lat <= 90:
                lat = np.radians(new_lat)
                print(f"Latitude atualizada para: {lat} radianos")
                glutPostRedisplay()  # Solicita o redesenho da tela
            else:
                print("A latitude deve estar entre -90 e 90 graus.")
        except ValueError:
            print("Por favor, insira um número válido.")


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    # TODO: FULLSCREEN
    glutInitWindowSize(width, height)
    glutCreateWindow(b"Cosmos")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(specialKeyboard)
    threading.Thread(target=get_new_lat, daemon=True).start()
    glutMainLoop()
 
if __name__ == "__main__":
    main()
