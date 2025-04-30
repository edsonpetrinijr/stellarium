from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math
import pandas as pd
import numpy as np

from Variables import *

from utils.rotate import rotate_point

def generate_points_on_sphere():
    global STARS, lat, lon, RADIUS, ORIGINAL
    
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
            ORIGINAL.append({
                'id': identifier,
                'original': {'position': np.array([x,y,z]), 'absolute_mag': mag-5*math.log10(1/parallax)+5,"distance_to_sun":RADIUS/parallax},
                # 'current': {'x': x, 'y': y, 'z': z, 'mag': mag, 'alpha': 1},
                'theta': theta, 'phi': phi, 'ra': ra, 'dec': dec,
                'parallax': parallax,
            })
    #id_star = "HD 187642"
    #reference_star = next(star for star in ORIGINAL if star['id'] == id_star)
    #position_reference_star = reference_star['original']['position']
    #rotated_position_reference_star, _, _ = rotate_point(position_reference_star, lat, lon)
    for star in ORIGINAL:
        orig = star['original']
        
        initial_position = orig['position']
        parallax = star['parallax']

        rotated_position, theta_new, phi_new = rotate_point(initial_position, lat, lon)        

        #real_target_position =rotated_position - rotated_position_reference_star
        real_target_position = rotated_position
        real_target_distance = np.linalg.norm(real_target_position)
    
        if real_target_distance != 0:
            mag = orig['absolute_mag']+math.log10(real_target_distance/RADIUS)-5
        else:
            mag = None
        
        STARS.append({
                'id': star['id'],
                'original': {'position': orig['position'], 'absolute_mag': orig['absolute_mag'],"distance_to_sun":orig['distance_to_sun']},
                'current': {'position': real_target_position,'alpha':1},
                'real_current': {'position': real_target_position, 'mag': mag,"distance_to_center":real_target_distance},
                'real_target': {'position': real_target_position,"distance_to_center":real_target_distance,'theta':theta_new,'phi':phi_new},
                'target': real_target_position,
                'target_alpha':1
            })

def recalc(go_to_star,lat,estrelas_esfera_celeste,estrelas_carta_celeste, id_star, projection_type):
    global STARS, lon, RADIUS, ORIGINAL
    if go_to_star:
        # ALNILAM
        # id_star = "HD 37128"

        # ALTAIR
        reference_star = next(star for star in ORIGINAL if star['id'] == id_star)
        position_reference_star = reference_star['original']['position']
        rotated_position_reference_star, _, _ = rotate_point(position_reference_star, lat, lon)
        
        for star in STARS:
            real_target = star['real_target']
            original = star['original']
            rotated_original,theta_new,phi_new = rotate_point(original['position'],lat,lon)
            real_target['theta'] = theta_new
            real_target['phi'] = phi_new

            real_target['position'] = rotated_original-rotated_position_reference_star
        
            real_target['distance_to_center'] = np.linalg.norm(real_target['position'])
            
            curr = star['current']
            real_current = star['real_current']
        
            if estrelas_esfera_celeste:
                if real_target['distance_to_center'] > 0.0001:
                    target_position = real_target['position']/real_target['distance_to_center']*RADIUS
                    target_alpha = 1
                else:
                    target_position = np.array([0,0,0])
                    target_alpha=0 
            elif estrelas_carta_celeste:
                if real_target['distance_to_center'] > 0.0001:
                    target_position = real_target['position']/real_target['distance_to_center']*RADIUS
                    target_alpha = 1
                else:
                    target_position = np.array([0,0,0])
                    target_alpha=0
                if target_position[2] > 0:
                    target_alpha = 1
                    theta_new = math.acos(real_target['position'][2]/real_target['distance_to_center'])
                    phi_new = math.atan2(real_target['position'][1],real_target['position'][0])
                    if projection_type == "orthographic":
                        target_position[2]=RADIUS
                    elif projection_type == "ayre":
            
                        factor = (2 * theta_new) / math.pi
                        target_position[0] = factor*RADIUS*math.cos(phi_new) 
                        target_position[1] = factor*RADIUS*math.sin(phi_new) 
                        target_position[2]=RADIUS
                    elif projection_type == "ayre_expanded":
                        target_position[0] =  theta_new*RADIUS*math.cos(phi_new) 
                        target_position[1] =  theta_new*RADIUS*math.sin(phi_new) 
                        target_position[2]=RADIUS
                    elif projection_type == "stereographic":
                        theta_new = real_target['theta']
                        target_position[2]=RADIUS
                        target_position[0] *= 2 *  math.tan(theta_new / 2)
                        target_position[1] *= 2 *  math.tan(theta_new / 2)
                else:
                    target_alpha = 0
            else:
                target_position = real_target['position']
                target_alpha = 1
            star['target']=target_position

            star['target_alpha'] = target_alpha
    else:
        for star in STARS:
            real_target = star['real_target']
            original = star['original']
            rotated_original,theta_new,phi_new = rotate_point(original['position'],lat,lon)

            real_target['position'] = rotated_original
            real_target['theta'] = theta_new
            real_target['phi'] = phi_new
        
            real_target['distance_to_center'] = np.linalg.norm(real_target['position'])
            curr = star['current']
            real_current = star['real_current']
        
            if estrelas_esfera_celeste:
                if real_target['distance_to_center'] > 0.01:
                    target_position = real_target['position']/real_target['distance_to_center']*RADIUS
                    target_alpha = 1
                else:
                    target_position = np.array([0,0,0])
                    target_alpha=0
            elif estrelas_carta_celeste:
                if real_target['distance_to_center'] > 0.01:
                    target_position = real_target['position']/real_target['distance_to_center']*RADIUS
                    target_alpha = 1
                else:
                    target_position = np.array([0,0,0])
                    target_alpha=0
                if target_position[2] > 0:
                    target_alpha = 1
                    theta_new = math.acos(real_target['position'][2]/real_target['distance_to_center'])
                    phi_new = math.atan2(real_target['position'][1],real_target['position'][0])
                    if projection_type == "orthographic":
                        target_position[2]=RADIUS
                    elif projection_type == "ayre":
            
                        factor = (2 * theta_new) / math.pi
                        target_position[0] = factor*RADIUS*math.cos(phi_new) 
                        target_position[1] = factor*RADIUS*math.sin(phi_new) 
                        target_position[2]=RADIUS
                    elif projection_type == "ayre_expanded":
                    
                        target_position[0] =  theta_new*RADIUS*math.cos(phi_new) 
                        target_position[1] =  theta_new*RADIUS*math.sin(phi_new) 
                        target_position[2]=RADIUS
                    elif projection_type == "stereographic":
                        theta_new = real_target['theta']
                        target_position[2]=RADIUS
                        target_position[0] *= 2 *  math.tan(theta_new / 2)
                        target_position[1] *= 2 *  math.tan(theta_new / 2)
                else:
                    target_alpha = 0
            else:
                target_position = real_target['position']
                target_alpha = 1
            star['target']=target_position

            star['target_alpha'] = target_alpha

    

def draw_stars(go_to_star, estrelas_esfera_celeste, estrelas_carta_celeste, star_color, lat, lon):
    global STARS, SPEED, projection_type, RADIUS, sun, ORIGINAL

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    for star in STARS:
        real_target = star['real_target']
        curr = star['current']
        real_current = star['real_current']
        target_alpha=star['target_alpha']
        target_position = star['target']
        THRESHOLD = 0.01
        dposition = target_position - curr['position']

        curr['position'] = target_position if np.linalg.norm(dposition) < THRESHOLD else curr['position'] + dposition * SPEED
        
        dreal_position = real_target['position'] - real_current['position'] 
        
        real_current['position'] = real_target['position'] if np.linalg.norm(dreal_position) < THRESHOLD else real_current['position']  + dreal_position * SPEED
        

        

        dalpha = target_alpha - curr['alpha']
        curr['alpha'] = target_alpha if abs(dalpha) < THRESHOLD else curr['alpha'] + dalpha * SPEED

        
        if curr['alpha'] > 0.01:
            real_current['distance_to_center'] = np.linalg.norm(real_current['position'])
            if real_current['distance_to_center'] > 0.01:
                real_current['mag'] = 10 * np.e ** (-0.33 * (star['original']['absolute_mag']+5*math.log10(real_current['distance_to_center']/RADIUS)-5))
            else:
                real_current['mag'] = 10 * np.e ** (-0.33 * (star['original']['absolute_mag']+5*math.log10(4.848e-6/RADIUS)-5))
            star_size = real_current['mag']
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