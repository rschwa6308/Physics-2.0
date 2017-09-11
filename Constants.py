from random import randint, uniform, shuffle
import pygame as pg
from pygame.math import Vector2 as V2
from math import hypot, pi, sin, cos, sqrt

G = 0.5

Density = 0.1

COR = 1.0 # Coefficient of Restitution

# Define initial width and height
pg.init()
info = pg.display.Info()
width, height = int(info.current_w * 0.6), int(info.current_h * 0.75)

# Set simulation hard clock speed (fps)
clock_speed = 144
