from random import randint
import pygame as pg
<<<<<<< HEAD
<<<<<<< HEAD
from pygame.math import Vector2 as V2
from math import hypot
=======
from math import atan2, sin, cos, hypot
>>>>>>> refs/remotes/rschwa6308/Single-Threading-Time-Control
=======
from math import atan2, sin, cos, hypot
from pygame.math import Vector2 as V2
from math import hypot
>>>>>>> refs/remotes/rschwa6308/Single-Threading-Time-Control

from Constants import *


class Body:
    def __init__(self, mass, position, velocity, density=Density, color=None):
        self.mass = mass
        self.radius = int((mass/density)**(1/3))

        self.position = V2(position)
        self.velocity = V2(velocity)

        self.density = density

        self.color = (randint(0, 255), randint(0, 255), randint(0, 255)) if color is None else color

        # self.image = pg.Surface((radius*2, radius*2))
        # self.image.fill(bg_color)
        # self.image.set_alpha(255)
        # pg.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius, 0)

    def draw_on(self, screen):
        pg.draw.circle(screen, self.color, (int(self.position[0]), int(self.position[1])), int(self.radius), 0)

<<<<<<< HEAD
<<<<<<< HEAD
    def force_of(self, other, G):
        x,y = (other.position[a]-self.position[a] for a in (0,1))
        r = hypot(x,y)
        acc = G/r**3
        return V2(acc * x, acc * y)

    def test_collision(self, other):
        return other.position.distance_to(self.position) < self.radius + other.radius # Zero-tolerance collision
        
=======
=======
>>>>>>> refs/remotes/rschwa6308/Single-Threading-Time-Control
    def effect_of(self, other, G):
        M = other.mass
        x_distance = other.position[0]-self.position[0]
        y_distance = other.position[1] - self.position[1]
        # distance_ratio = float(x_distance) / float(y_distance)
        r = hypot(x_distance, y_distance)
        angle = atan2(y_distance, x_distance)
        magnitude = (G * M) / (r ** 2)
        x_accel = magnitude * cos(angle)
        y_accel = magnitude * sin(angle)
        # set a ceiling on body acceleration
        x_accel = min(x_accel, 100)
        y_accel = min(y_accel, 100)

        return (x_accel , y_accel)

    def test_collision(self, other):
        return hypot(abs(other.position[0] - self.position[0]), abs(other.position[1] - self.position[1])) < (self.radius + other.radius) * 1.0        #'...) * 0.5' gives collosion tolerance equal to the mean radius, '1.0' gives zero-tolerance

<<<<<<< HEAD
>>>>>>> refs/remotes/rschwa6308/Single-Threading-Time-Control
=======
    def force_of(self, other, G):
        x,y = (other.position[a]-self.position[a] for a in (0,1))
        r = hypot(x,y)
        acc = G/r**3
        return V2(acc * x, acc * y)

    def test_collision(self, other):
        return other.position.distance_to(self.position) < self.radius + other.radius # Zero-tolerance collision

>>>>>>> refs/remotes/rschwa6308/Single-Threading-Time-Control
    def merge(self, other):
        total_mass = self.mass + other.mass
        self.position = (self.position*self.mass + other.position*other.mass) / total_mass
        self.velocity = (self.velocity*self.mass + other.velocity*other.mass) / total_mass

        avg_density = (self.density * self.mass + other.density * other.mass) / total_mass
        self.radius = int((total_mass/avg_density)**(1/3))

        self.color = tuple(((self.color[x]*self.mass + other.color[x]*other.mass)/total_mass) for x in (0,1,2))

        self.mass = total_mass

    def apply_acceleration(self, acceleration):
        self.velocity += acceleration

    def apply_velocity(self, time_factor):
        self.position += self.velocity * time_factor
