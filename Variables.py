import numpy as np
import math

TARGET_Y = 100
SPEED = 2.0 
RADIUS = 100  # Tamanho da esfera
THRESHOLD = 1  # Tolerância para considerar que a estrela chegou ao destino
finished = False  # Flag global para evitar prints repetidos
# Variável global de controle
move_camera = False

POINTS = []

camera_carta_celeste = False
camera_lateral = False
camera_heitor = False

# 4821,HD 34085,s*b,-0.1431455934,np.degrees(),3.78,0.13
lat = 0.1431455934 + math.pi
lon = -(1.372430356 - math.pi)

stars_data = []
red = 0.05
green = 0.05
blue = 0.1
star_color = (1, 1, 1)

fov = 60.0
width, height = 600, 600
last_x = 0
last_y = 0
yaw = 0.0
pitch = 0.0
mouse_down = False
move = False

target_yaw = 0.0
target_pitch = 0.0
start_yaw = 0.0
start_pitch = 0.0
t = 0.0
delta = 0.075
# PADRÃO 10
viewer_height = 0
go_to_star = False

recording = False
frames = []

estrelas_carta_celeste = False


original_points = []



desenhar_chao = True
desenhar_grade_equatorial = True
visao_carta_celeste = False

desenhar_grade_azimutal = False

animacao_rodando = False

animation_queue = []
estrelas_posicao_real = False

