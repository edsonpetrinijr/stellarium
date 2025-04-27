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
                'original': {
                    'position': np.array([x, y, z]),
                    'distance': RADIUS / parallax,
                    'mag': mag,
                    'alpha': 1,
                    'absolute_mag': mag - 5 * math.log10(1 / parallax) + 5,
                },
                'current': { 
                    'position': np.array([x, y, z]),
                    'real_position': np.array([x, y, z]),
                    'distance': RADIUS / parallax,
                    'mag': mag,
                    'alpha': 1,
                }
            })

        # STARS.append({
        #     'id': "Sol",
        #     'original': {'x': 0, 'y': 0, 'z': 0, 'mag': 0, 'alpha': 0},
        #     'current': {'x': 0, 'y': 0, 'z': 0, 'mag': 0, 'alpha': 0},
        #     'theta': 0, 'phi': 0, 'ra': 0, 'dec': 0,
        #     'parallax': 0,
        #     })


def draw_stars(go_to_star, estrelas_esfera_celeste, estrelas_carta_celeste, star_color, lat, lon):
    global STARS, SPEED, projection_type, RADIUS, sun, THRESHOLD

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
   
    id_star = "HD 48915"
    reference_star = next(star for star in STARS if star['id'] == id_star)
    position_reference_star = reference_star['original']['position']

    # distance_reference_star = reference_star['distance']
    
    position_reference_star, _, _ = rotate_point(position_reference_star, lat, lon)

    for star in STARS:
        orig = star['original']
        curr = star['current']
        
        original_position = orig['position']
        target_distance = orig['distance']

        target_position, theta_new, phi_new = rotate_point(original_position, lat, lon)        

        if go_to_star:
            target_position = target_position - position_reference_star
            target_distance = np.linalg.norm(target_position)
            
            if (star['id'] != id_star):
                theta_new = math.acos(target_position[2] / target_distance)
        
                target_mag = orig['mag'] - 5 * (math.log10(target_distance / target_distance))
            else:
                if curr['distance'] < THRESHOLD:
                    target_mag = 4
                else:
                    target_mag = -15
        else:
            target_mag = orig['mag']
        
        current_real_position = target_position.copy()
        
        if estrelas_esfera_celeste:
            target_position *= RADIUS / target_distance 
            
            target_alpha = 1
        elif estrelas_carta_celeste:
            target_position *= RADIUS / target_distance 
            
            if target_position[2] > 0:
                target_alpha = 1

                if projection_type == "orthographic":
                    target_position[2] = RADIUS
                elif projection_type == "ayre":
                    target_position *= (2 * theta_new) / math.pi
                    target_position[2] = RADIUS
                elif projection_type == "ayre_expanded":
                    target_position *= theta_new
                    target_position[2] = RADIUS
                elif projection_type == "stereographic":
                    target_position *= 2 * math.tan(theta_new / 2) 
                    target_position[2] = RADIUS
            else:
                target_alpha = 0
        else:
            target_alpha = 1

        THRESHOLD = 0.01

        dposition = target_position - curr['position']
        curr['position'] = target_position if np.linalg.norm(dposition) < THRESHOLD else curr['position'] + dposition * SPEED
        curr['real_position'] = current_real_position
        curr['distance'] = np.linalg.norm(curr['real_position'])
        
        # dmag = target_mag - curr['mag']
        # curr['mag'] = target_mag if abs(dmag) < THRESHOLD else curr['mag'] + dmag * SPEED

        dalpha = target_alpha - curr['alpha']
        curr['alpha'] = target_alpha if abs(dalpha) < THRESHOLD else curr['alpha'] + dalpha * SPEED

        if curr['alpha'] > THRESHOLD:
            # star_size = 10 * np.e ** (-0.33 * curr['mag'])
            if (curr['distance'] != 0):
                star_size = 10 * np.e ** (-0.33 * (orig['absolute_mag']+5*math.log10(curr['distance']/RADIUS)-5))
                glPointSize(star_size)
                glBegin(GL_POINTS)
                glColor4f(*star_color, curr['alpha'])
                glVertex3f(*curr['position'])
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