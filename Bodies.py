from random import randint
import pygame as pg
from pygame.math import Vector2 as V2
from math import atan2, sin, cos, hypot

from Colors import *
from Constants import *


class Body:
    def __init__(self, mass, position, velocity, density=Density, color=None):
        self.mass = mass
        self.radius = int((mass/density)**(1/3))

        self.position = position
        self.velocity = velocity

        self.density = density

        self.color = (randint(0, 255), randint(0, 255), randint(0, 255)) if color is None else color

        # self.image = pg.Surface((radius*2, radius*2))
        # self.image.fill(bg_color)
        # self.image.set_alpha(255)
        # pg.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius, 0)

    def draw_on(self, screen):
        pg.draw.circle(screen, self.color, (int(self.position[0]), int(self.position[1])), self.radius, 0)

    def effect_of(self, other, G):
        M = other.mass
        x_distance = other.position[0]-self.position[0]
        y_distance = other.position[1] - self.position[1]
        r = hypot(x_distance, y_distance)
        angle = atan2(y_distance, x_distance)
        magnitude = (G * M) / (r ** 2)
        x_accel = magnitude * cos(angle)
        y_accel = magnitude * sin(angle)
        # set a ceiling on body acceleration
        # x_accel = min(x_accel, 100)
        # y_accel = min(y_accel, 100)

        return (x_accel , y_accel)

    def test_collision(self, other):
        return V2(other.position).distance_to(self.position) < self.radius + other.radius # Zero-tolerance collision
        
    def merge(self, other):
        # print "merge!"
        total_mass = self.mass + other.mass
        self.position = [(self.position[x]*self.mass + other.position[x]*other.mass) / total_mass for x in (0,1)]
        self.velocity = [(self.velocity[x]*self.mass + other.velocity[x]*other.mass) / total_mass for x in (0,1)]

<<<<<<< HEAD
        avg_density = (self.density * self.mass + other.density * other.mass) / total_mass
        self.radius = int((total_mass/avg_density)**(1/3))
=======
        avg_density = (self.density * self.mass + other.density * other.mass) / (self.mass + other.mass)
        self.radius = max(max(int(round(((self.mass + other.mass) / avg_density) ** 0.333333)), self.radius), other.radius)
>>>>>>> refs/remotes/rschwa6308/master

        self.color = tuple(((self.color[x]*self.mass + other.color[x]*other.mass)/total_mass) for x in (0,1,2))

        self.mass = total_mass

    def apply_acceleration(self, acceleration):
        self.velocity[0] += acceleration[0]
        self.velocity[1] += acceleration[1]

    def apply_velocity(self):
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
