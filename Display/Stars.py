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






# def generate_points_on_sphere():
#     global POINTS, original_points, lat, lon, stars_data
#     csv_path = 'stars_data.csv'

#     df = pd.read_csv(csv_path)
#     df = df.groupby('Constellation').head(20)

#     for _, row in df.iterrows():
#         try:
#             dec = dec_to_deg(row['Declination'])
#             ra = ra_to_deg(row['Right Ascension'])
#             mag = row['Apparent Magnitude']
#         except Exception as e:
#             print(f"Erro ao processar {row.get('Name', 'estrela desconhecida')}: {e}")
#             continue
        
#         theta = np.radians(90 - dec)
#         phi = np.radians(ra - 90)

#         x = -RADIUS * math.sin(theta) * math.cos(phi)
#         y = RADIUS * math.cos(theta)
#         z = RADIUS * math.sin(theta) * math.sin(phi)
    
#         star_size = 10 * np.e ** (-0.33 * mag)

#         stars_data.append((x,y,z,star_size, theta, phi, ra, dec, 1, mag))
#     # original_points = copy.deepcopy(POINTS)
#     POINTS = copy.deepcopy(stars_data)

def draw_stars(go_to_star, estrelas_posicao_real, estrelas_carta_celeste, star_color, lat, lon):
    global POINTS, stars_data, RADIUS, SPEED, projection_type

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
    ) = [point for point in stars_data if point[0] == "HD 187642"][0]
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
        ) = stars_data[i]

        (identifier, x, y, z, star_size, theta, phi, ra, dec, alpha, mag, plx) = POINTS[i]
        
        if go_to_star:
            target_x, target_y, target_z, theta_new, phi_new = rotate_point(x_original, y_original, z_original, lat, lon)

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
            star_size = 10 * np.e ** (-0.33 * mag_new)
        elif estrelas_posicao_real:
            target_x, target_y, target_z, theta_new, phi_new = rotate_point(x_original, y_original, z_original, lat, lon)
            target_x /= plx
            target_y /= plx
            target_z /= plx

            star_size = 10 * np.e ** (-0.33 * mag)
        else:
            target_x, target_y, target_z, theta_new, phi_new = rotate_point(x_original, y_original, z_original, lat, lon)

            star_size = 10 * np.e ** (-0.33 * mag)

        # dx = target_x - x
        # dy = target_y - y
        # dz = target_z - z

        # x += dx * 0.05 * SPEED
        # y += dy * 0.05 * SPEED
        # z += dz * 0.05 * SPEED


        # if alpha < 1:
        #     alpha = min(1, alpha + 0.05 * SPEED)

        if estrelas_carta_celeste:
            if target_z > 0:
                alpha=1
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
                    target_x = 2*RADIUS * math.tan(theta_new/2) * math.sin(phi_new)
                    target_y = 2*RADIUS * math.tan(theta_new/2) * math.cos(phi_new)
                    target_z = RADIUS
                else:
                    print("n tem")

                dx = target_x - x
                dy = target_y - y
                dz = target_z - z

                x += dx * 0.05 * SPEED
                y += dy * 0.05 * SPEED
                z += dz * 0.05 * SPEED
            
            # elif alpha > 0:
            #     alpha = max(0, alpha - 0.05 * SPEED)
            else:
                alpha = 0

            new_points.append((identifier, x, y, z, star_size, theta, phi, ra, dec, alpha, mag, plx))
        else:
            dx = target_x - x
            dy = target_y - y
            dz = target_z - z

            x += dx * 0.05 * SPEED
            y += dy * 0.05 * SPEED
            z += dz * 0.05 * SPEED
            alpha=1

            new_points.append((identifier, x, y, z, star_size, theta_new, phi_new, ra, dec, alpha, mag, plx))


        glPointSize(star_size)
        glBegin(GL_POINTS)
        glColor4f(*star_color, alpha)
        glVertex3f(x, y, z)
        glEnd()

    POINTS = new_points

    glDisable(GL_BLEND)
    glutPostRedisplay()
