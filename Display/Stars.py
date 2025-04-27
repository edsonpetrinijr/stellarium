from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math
import pandas as pd
import numpy as np

from Variables import *

from utils.rotate import rotate_point

def generate_points_on_sphere():
    global STARS, lat, lon, RADIUS
    
    df = pd.read_csv('data.csv')

    for _, row in df.iterrows():
        try:
            identifier = row['identifier']
            dec = float(row['DEC (rad)'])
            ra = float(row['RA (rad)'])
            mag = float(row['Mag V (mag)'])
            parallax = float(row['plx (mas)']) / 1000
        except Exception as e:
            print(f"Erro ao processar {row.get('Name', 'estrela desconhecida')}: {e}")
            continue
        
        theta = np.pi / 2 - dec
        phi = ra - np.pi / 2

        x = RADIUS * math.sin(theta) * math.cos(phi) / parallax
        y = RADIUS * math.sin(theta) * math.sin(phi) / parallax
        z = RADIUS * math.cos(theta) / parallax
    
        # star_size = 10 * np.e ** (-0.33 * mag)

        if (mag < 5):
            STARS.append({
                'id': identifier,
                'original': {'x': x, 'y': y, 'z': z, 'mag': mag, 'alpha': 1},
                'current': {'x': x, 'y': y, 'z': z, 'mag': mag, 'alpha': 1},
                'theta': theta, 'phi': phi, 'ra': ra, 'dec': dec,
                'parallax': parallax,
            })
        # STARS.append({
        #     'id': "Sol",
        #     'original': {'x': 0, 'y': 0, 'z': 0, 'mag': 0, 'alpha': 0},
        #     'current': {'x': 0, 'y': 0, 'z': 0, 'mag': 0, 'alpha': 0},
        #     'theta': 0, 'phi': 0, 'ra': 0, 'dec': 0,
        #     'parallax': 0,
        #     })

def draw_stars(go_to_star, estrelas_esfera_celeste, estrelas_carta_celeste, star_color, lat, lon):
    global STARS, SPEED, projection_type, RADIUS, sun

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
   
    id_star = "HD 187642"
    reference_star = next(star for star in STARS if star['id'] == id_star)
    x_reference_star = reference_star['original']['x']
    y_reference_star = reference_star['original']['y']
    z_reference_star =  reference_star['original']['z']

    parallax_reference_star = reference_star['parallax']
    
    x_reference_star, y_reference_star, z_reference_star, _, _ = rotate_point(x_reference_star, y_reference_star, z_reference_star, lat, lon)

    for star in STARS:
        orig = star['original']
        curr = star['current']
        
        x0, y0, z0 = orig['x'], orig['y'], orig['z']
        parallax = star['parallax']

        target_x, target_y, target_z, theta_new, phi_new = rotate_point(x0, y0, z0, lat, lon)        

        if go_to_star:
            target_x -= x_reference_star
            target_y -= y_reference_star
            target_z -= z_reference_star
            
            # REF
            star_array = np.array([target_x, target_y, target_z])
            new_star_distance = np.linalg.norm(star_array)
            
            # if target_x != 0 and target_y != 0 and target_z != 0:
            if (star['id'] != id_star):
                theta_new = math.acos(target_z / new_star_distance)
                phi_new = math.atan2(target_y, target_x)
                target_mag = orig['mag'] - 5 * (math.log10(RADIUS / (new_star_distance * parallax)))
                # star_size_target = 10 * np.e ** (-0.33 * mag_new)

                # target_x /= new_star_distance / 100
                # target_y /= new_star_distance / 100
                # target_z /= new_star_distance / 100
            else:
                if curr['x'] < 0.1 and curr['y'] < 0.1 and curr['z'] < 0.1:
                    target_mag = 4
                else:
                    target_mag = -15
                    
            # else:
            #     star_size_target = 10 * np.e ** (-0.33 * -10)

            #     
            #         star_size_target = 10 * np.e ** (-0.33 * 5)
        else:
            target_mag = orig['mag']
            if (star['id'] == id_star):
                print(orig['x'], curr['x'])
    
        if estrelas_esfera_celeste:
            target_x *= parallax
            target_y *= parallax
            target_z *= parallax
            
            target_alpha = 1
        elif estrelas_carta_celeste:
            target_x *= parallax
            target_y *= parallax
            target_z *= parallax
            
            if target_z > 0:
                target_alpha = 1
                if projection_type == "orthographic":
                    target_z = RADIUS
                elif projection_type == "ayre":
                    factor = (2 * theta_new) / math.pi
                    target_x = RADIUS * factor * math.cos(phi_new)
                    target_y = RADIUS * factor * math.sin(phi_new)
                    target_z = RADIUS
                elif projection_type == "ayre_expanded":
                    target_x = RADIUS * theta_new * math.cos(phi_new)
                    target_y = RADIUS * theta_new * math.sin(phi_new)
                    target_z = RADIUS
                elif projection_type == "stereographic":
                    target_x = 2 * RADIUS * math.tan(theta_new / 2) * math.cos(phi_new)
                    target_y = 2 * RADIUS * math.tan(theta_new / 2) * math.sin(phi_new)
                    target_z = RADIUS
            else:
                target_alpha = 0
        else:
            target_alpha = 1

        THRESHOLD = 0.01

        dx = target_x - curr['x']
        dy = target_y - curr['y']
        dz = target_z - curr['z']

        curr['x'] = target_x if abs(dx) < THRESHOLD else curr['x'] + dx * SPEED
        curr['y'] = target_y if abs(dy) < THRESHOLD else curr['y'] + dy * SPEED
        curr['z'] = target_z if abs(dz) < THRESHOLD else curr['z'] + dz * SPEED

        dmag = target_mag - curr['mag']
        curr['mag'] = target_mag if abs(dmag) < THRESHOLD else curr['mag'] + dmag * SPEED

        dalpha = target_alpha - curr['alpha']
        curr['alpha'] = target_alpha if abs(dalpha) < THRESHOLD else curr['alpha'] + dalpha * SPEED

        
        if curr['alpha'] > 0.01:
            star_size = 10 * np.e ** (-0.33 * curr['mag'])
            glPointSize(star_size)
            glBegin(GL_POINTS)
            glColor4f(*star_color, curr['alpha'])
            glVertex3f(curr['x'], curr['y'], curr['z'])
            glEnd()

    glDisable(GL_BLEND)
    glutPostRedisplay()

"""
    orig_sun = sun['original']
    curr_sun = sun['current']
    if go_to_star:
        target_x_sun = -x_reference_star
        target_y_sun = -y_reference_star
        target_z_sun = -z_reference_star
        target_mag_sun = 4.83 + 5*math.log10(1/parallax_reference_star)-5
        target_alpha_sun=1
    else:
        target_x_sun = 0
        target_y_sun = 0
        target_z_sun = 0
        target_alpha_sun= 0
        
        # dsize = star_size_target - curr['size']
        # curr['size'] += dsize * SPEED
        
    dx_sun = target_x_sun - curr_sun['x']
    dy_sun = target_y_sun - curr_sun['y']
    dz_sun = target_z_sun - curr_sun['z']

    curr_sun['x'] += dx_sun * SPEED
    curr_sun['y'] += dy_sun * SPEED
    curr_sun['z'] += dz_sun * SPEED
    
    dmag_sun = target_mag_sun - curr_sun['mag']
    curr_sun['mag'] += dmag_sun * SPEED

    dalpha_sun = target_alpha_sun - curr_sun['alpha']
    curr_sun['alpha'] += dalpha_sun * SPEED
    
    if curr_sun['alpha'] > 0.01:
        sun_size = 10 * np.e ** (-0.33 * curr_sun['mag'])
        glPointSize(sun_size)
        glBegin(GL_POINTS)
        if (star['id'] != 'Sun'):
            glColor4f(*star_color, curr_sun['alpha'])
        else: 
            glColor4f((1, 1, 0), curr_sun['alpha'])
        glVertex3f(curr_sun['x'], curr_sun['y'], curr_sun['z'])
        glEnd()
            
"""