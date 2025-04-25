import copy
from PIL import Image
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math
import pandas as pd
import numpy as np

from animation.lerp_angle import *
from animation.ease_in_out import *

from Display.CelestialSphere import *
from Display.Ground import *
from Variables import *
# from video.save_video import *
from Display.Stars import *
from Display.Grid import *
from Display.AzimutalGrid import *

from utils.conversions import *


import threading

def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_POINT_SMOOTH)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
    generate_points_on_sphere()

def display():
    global RADIUS, desenhar_chao, desenhar_grade_equatorial, visao_carta_celeste, animacao_rodando,desenhar_grade_azimutal, lat, lon, is_fullscreen, estrelas_carta_celeste, estrelas_posicao_real, go_to_star
    global camera_carta_celeste, camera_lateral
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

    if (visao_carta_celeste):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspect = width / height if height != 0 else 1
        size = RADIUS + 5 # quanto maior, mais "zoom out"

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
        draw_equatorial_sphere_grid(lat)
    if desenhar_grade_azimutal:
        draw_sphere_grid()

    # lon += 0.01
    # if (lon >= 180):
    #     lon = -180

    draw_stars(go_to_star, estrelas_posicao_real, estrelas_carta_celeste, star_color, lat, lon)

    RIGEL = (88.79287500000001, 7.4070277777777775)
    BETELGEUSE = (78.63445833333334, -8.201638888888889)
    ANTARES = (247.35195833333333, -26.431944444444444)

    # move_to_ra_dec(*RIGEL)
 
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
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        visao_carta_celeste = not visao_carta_celeste
    elif button == 3:
        zoom_in()
    elif button == 4:
        zoom_out()

def zoom_in():
    global fov
    fov = max(10, fov - 2)
    update_projection()
    glutPostRedisplay()

def zoom_out():
    global fov
    fov = min(100, fov + 2)
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
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, 4000, 4000, GL_RGB, GL_UNSIGNED_BYTE)
    image = Image.frombytes("RGB", (4000, 4000), data)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)

    image = crop_black_borders(image)

    image.save(filename)
    print(f"Imagem salva como {filename}")


def keyboard(key, x, y):
    global estrelas_carta_celeste, desenhar_chao, desenhar_grade_equatorial, animacao_rodando,animation_queue,desenhar_grade_azimutal, red, green, blue, star_color, estrelas_posicao_real, viewer_height, go_to_star
    global camera_lateral, camera_carta_celeste, camera_heitor
    global is_fullscreen
    if key == b'c':
        estrelas_carta_celeste = not estrelas_carta_celeste
        print(estrelas_carta_celeste)
        visao_carta_celeste = True
    elif key == b'1':
        camera_carta_celeste = not camera_carta_celeste
    elif key == b'2':
        camera_lateral = not camera_lateral
    elif key == b'3':
        camera_heitor = not camera_heitor
    elif key == b's':
        save_screenshot()
    elif key == b'e':
        desenhar_grade_equatorial = not desenhar_grade_equatorial
    elif key == b'g':
        desenhar_chao = not desenhar_chao
    # elif key == b'a':
    #     animation_queue.append((88.79287500000001, 7.4070277777777775))  # RIGEL

    #     animation_queue.append((78.63445833333334, -8.201638888888889))  # BETELGEUSE
    #     animacao_rodando = True
    elif key == b'h':
        # if viewer_height == 0:
        #     viewer_height = 10
        # else:
        #     viewer_height = 0
        estrelas_posicao_real = not estrelas_posicao_real
    elif key == b'm':
        go_to_star = not go_to_star
    elif key == b'z':
        desenhar_grade_azimutal = not desenhar_grade_azimutal
    elif key == b'i':
        if (not red == 1):
            red, green, blue = 1, 1, 1
            star_color = (0,0,0)
        else:
            red = 0.05
            green = 0.05
            blue = 0.1
            star_color = (1,1,1)

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
    glutInitWindowSize(width, height)
    glutCreateWindow(b"Cosmos")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)  
    glutKeyboardFunc(keyboard)
    threading.Thread(target=get_new_lat, daemon=True).start()
    glutMainLoop()
 
if __name__ == "__main__":
    main()
