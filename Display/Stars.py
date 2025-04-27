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

def generate_points_on_sphere():
    global POINTS, stars_data, lat, lon
    
    df = pd.read_csv('data.csv')

    for _, row in df.iterrows():
        try:
            identifier = row['identifier']
            dec = float(row['DEC (rad)'])
            ra = float(row['RA (rad)'])
            mag = float(row['Mag V (mag)'])
            plx = float(row['plx (mas)']) / 1000
        except Exception as e:
            print(f"Erro ao processar {row.get('Name', 'estrela desconhecida')}: {e}")
            continue
        
        theta = np.pi / 2 - dec
        phi = ra - np.pi / 2

        x = RADIUS * math.sin(theta) * math.cos(phi)
        y = RADIUS * math.sin(theta) * math.sin(phi)
        z = RADIUS * math.cos(theta)
    
        star_size = 10 * np.e ** (-0.33 * mag)

        if mag < 5:
            stars_data.append((identifier, x,y,z,star_size, theta, phi, ra, dec, 1, mag, plx))

    POINTS = copy.deepcopy(stars_data)

def draw_stars(go_to_star, estrelas_posicao_real, estrelas_carta_celeste, star_color, lat, lon):
    global POINTS, stars_dataSPEED, projection_type, sol

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
        plx_star
    ) = [point for point in stars_data if point[0] == "HD 37128"][0]
    # ALNILAM
    # ) = [point for point in stars_data if point[0] == "HD 37128"][0]
    #Altair
    #= [point for point in stars_data if point[0] == "HD 187642"][0]
    
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
        ) = stars_data[i]

        (identifier, x, y, z, star_size, theta, phi, ra, dec, alpha, mag, plx) = POINTS[i]
        
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
            if target_x!=0 and target_y!=0 and target_z!=0:
                r = np.linalg.norm(ponto)
                theta_new = math.acos(target_z / r)
                phi_new = math.atan2(target_y, target_x)
                mag_new = mag - 5 * (math.log10(RADIUS / (r * plx)))
                star_size_target = 10 * np.e ** (-0.33 * mag_new)
                target_x /= r/100
                target_y /= r/100
                target_z /= r/100
            else:
                star_size_target = 10 * np.e ** (-0.33 * -10)
                if x<0.1 and y < 0.1 and z <0.1:
                    star_size_target = 10 * np.e ** (-0.33 * 5)
            

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
        
        new_points.append((identifier, x, y, z, star_size, theta_new, phi_new, ra, dec, alpha, mag, plx))
        
        if alpha > 0.01:
            glPointSize(star_size)
            glBegin(GL_POINTS)
            glColor4f(*star_color, alpha)
            glVertex3f(x, y, z)
            glEnd()
            


    POINTS = new_points

    glDisable(GL_BLEND)
    glutPostRedisplay()
    
"""    if go_to_star:
        x_star_test  = x_star / plx_star
        y_star_test  = y_star / plx_star
        z_star_test  = z_star / plx_star
        
        target_x_sun = - x_star_test
        target_y_sun = - y_star_test
        target_z_sun = - z_star_test
        ponto = np.array([target_x_sun, target_y_sun, target_z_sun])
        r_sun = np.linalg.norm(ponto)  
        mag_new = mag + 5 * (math.log10(r))-5
        sun_size_target = 10 * np.e ** (-0.33 * mag_new)
        sun_size_target = 1
        sun_alpha_target = 1
    else: 
        target_x_sun = 0
        target_y_sun = 0
        target_z_sun = 0
        sun_size_target = 0.01
        sun_alpha_target = 0
    x_sun = sol[0]
    y_sun= sol[1]
    z_sun= sol[2]
    dx = target_x_sun - x_sun
    dy = target_y_sun - y_sun
    dz = target_z_sun - z_sun

    x_sun += dx * SPEED
    y_sun += dy * SPEED
    z_sun += dz * SPEED
    sun_size = sol[3]
    sun_alpha = sol[4]
    dsize = sun_size_target - sun_size
    sun_size += dsize * SPEED
    
    dalpha = sun_alpha_target - sun_alpha
    sun_alpha += dalpha * SPEED
    
    glPointSize(sun_size)
    glBegin(GL_POINTS)
    glColor4f(*star_color, sun_alpha)
    glVertex3f(x_sun, y_sun, z_sun)
    glEnd()
    sol = [x_sun,y_sun,z_sun,sun_size,sun_alpha]
"""
