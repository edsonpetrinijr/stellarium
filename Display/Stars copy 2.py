import copy
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math
import pandas as pd
import numpy as np

from animation.lerp_angle import *
from animation.ease_in_out import *

from main import * 
from utils.rotate import rotate_point

def stellar_class_to_glcolor(temperature: int) -> tuple[float, float, float]:
    """
    Converte a temperatura de uma estrela em Kelvin para uma cor RGB normalizada.
    A conversão é uma aproximação, usando o modelo de Black Body Radiation.
    """
    # Garantir que a temperatura esteja dentro de um intervalo razoável
    if temperature < 1000 or temperature > 40000:
        r = 255
        g = 255
        b = 255

    # Aproximações para a temperatura da estrela (simplificado)
    if temperature <= 6600:
        # Estrelas mais frias (vermelhas/laranja)
        r = 255
        g = int((temperature - 1000) / 5600 * 255)
        b = int((temperature - 1000) / 6600 * 255)
    else:
        # Estrelas mais quentes (brancas/azuladas)
        r = int(255 - ((temperature - 6600) / 34000 * 255))
        g = int(255 - ((temperature - 6600) / 34000 * 255))
        b = 255

    # Normalizando os valores de RGB para a faixa [0, 1]
    return (r / 255, g / 255, b / 255)

def hms_to_rad(hours, minutes, seconds):
    """Converte horas:minutos:segundos para radianos"""
    total_hours = float(hours) + float(minutes) / 60 + float(seconds) / 3600
    return math.radians(total_hours * 15)

def dms_to_rad(sign, degrees, minutes, seconds):
    """Converte graus:minutos:segundos com sinal para radianos"""
    total_degrees = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
    if sign == '-':
        total_degrees *= -1
    return math.radians(total_degrees)

import json
with open('bsc5-all.json', encoding="utf8") as f:
    data = json.load(f)

def generate_points_on_sphere():
    global POINTS, stars_data, lat, lon
    
    for row in data:
        try:
            identifier = row.get('Common', '') 
            ra = hms_to_rad(row['RAh'], row['RAm'], row['RAs'])
            dec = dms_to_rad(row['DE-'], row['DEd'], row['DEm'], row['DEs'])
            mag = float(row['Vmag'])
            plx = float(row.get('Parallax', 0)) / 1000
            spectral_type = float(row['K'])
        except Exception as e:
            print("Deu erro")
    
        theta = np.pi / 2 - dec
        phi = ra - np.pi / 2

        x = RADIUS * math.sin(theta) * math.cos(phi)
        y = RADIUS * math.sin(theta) * math.sin(phi)
        z = RADIUS * math.cos(theta)
    
        star_size = 10 * np.e ** (-0.33 * mag)
        star_color = stellar_class_to_glcolor(spectral_type)

        if mag < 5 and plx != 0:
            stars_data.append((identifier, x,y,z,star_size, theta, phi, ra, dec, 1, mag, plx, star_color))

    POINTS = copy.deepcopy(stars_data)
    print(stars_data)

def draw_stars(go_to_star, estrelas_posicao_real, estrelas_carta_celeste, lat, lon):
    global POINTS, stars_dataSPEED, projection_type

    new_points = []

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
   
    (
        identifier_star,
        x_star,
        y_star,
        z_star,
        size_star,
        theta_star,
        phi_star,
        ra_star,
        dec_star,
        alpha_star,
        mag_star,
        plx_star,
        star_color_star
    ) = [point for point in stars_data if point[0] == "Antares"][0]
    # ALNILAM
    # ) = [point for point in stars_data if point[0] == "HD 37128"][0]
    
    x_star, y_star, z_star, theta_star, phi_star = rotate_point(x_star, y_star, z_star, lat, lon)

    for i in range(len(POINTS)):
        (
            identifier_original,
            x_original,
            y_original,
            z_original,
            size_original,
            theta_original,
            phi_original,
            ra_original,
            dec_original,
            alpha_original,
            mag_original,
            plx_original,
            star_color_original
        ) = stars_data[i]

        (identifier, x, y, z, star_size, theta, phi, ra, dec, alpha, mag, plx, star_color) = POINTS[i]
        
        target_x, target_y, target_z, theta_new, phi_new = rotate_point(x_original, y_original, z_original, lat, lon)

        if go_to_star:
            x_original_test = target_x / plx_original
            y_original_test = target_y / plx_original
            z_original_test = target_z / plx_original
        
            x_star_test  = x_star / plx_star
            y_star_test  = y_star / plx_star
            z_star_test  = z_star / plx_star        
            
            target_x, target_y, target_z = (x_original_test - x_star_test), (y_original_test - y_star_test), (z_original_test - z_star_test)
            ponto = np.array([target_x, target_y, target_z])
            r = np.linalg.norm(ponto)
            theta_new = math.acos(target_z / r)
            phi_new = math.atan2(target_y, target_x)
            if r != 0:
                mag_new = mag - 5 * (math.log10(RADIUS / (r * plx)))
            star_size_target = 10 * np.e ** (-0.33 * mag_new)
            target_x /= r/100
            target_y /= r/100
            target_z /= r/100
        else:
            star_size_target = 10 * np.e ** (-0.33 * mag)

        if estrelas_carta_celeste:
            if target_z > 0:
                alpha_target = 1
                factor = (2 * theta_new) / math.pi
                if projection_type == "orthographic":
                    target_z = RADIUS
                elif projection_type == "ayre":
                    target_x = RADIUS * factor * math.cos(phi_new)
                    target_y = RADIUS * factor * math.sin(phi_new)
                    target_z = RADIUS
                elif projection_type == "ayre_expanded":
                    target_x = RADIUS * theta_new * math.cos(phi_new)
                    target_y = RADIUS * theta_new * math.sin(phi_new)
                    target_z = RADIUS
                elif projection_type == "stereographic":
                    target_x = 2*RADIUS * math.tan(theta_new/2) * math.cos(phi_new)
                    target_y = 2*RADIUS * math.tan(theta_new/2) * math.sin(phi_new)
                    target_z = RADIUS
                else:
                    print("n tem")
            else:
                alpha_target = 0
        elif estrelas_posicao_real:
            target_x /= plx
            target_y /= plx
            target_z /= plx
            if target_z < 0 and estrelas_carta_celeste:
                alpha_target = 0
            else:
                alpha_target = 1
        else:
            alpha_target = 1

        dx = target_x - x
        dy = target_y - y
        dz = target_z - z

        x += dx * SPEED
        y += dy * SPEED
        z += dz * SPEED
        
        dsize = star_size_target - star_size
        star_size += dsize * SPEED
        
        dalpha = alpha_target - alpha
        alpha += dalpha * SPEED
        
        new_points.append((identifier, x, y, z, star_size, theta_new, phi_new, ra, dec, alpha, mag, plx, star_color))
        
        if alpha > 0.01:
            glPointSize(star_size)
            glBegin(GL_POINTS)
            glColor4f(*star_color, alpha)
            glVertex3f(x, y, z)
            glEnd()

    POINTS = new_points

    glDisable(GL_BLEND)
    glutPostRedisplay()
