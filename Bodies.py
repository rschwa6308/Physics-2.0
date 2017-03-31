from random import randint
import pygame as pg
from math import atan2, sin, cos

from Colors import *
from Constants import *


class Body:
    def __init__(self, mass, radius, position, velocity, color=None):
        self.mass = mass
        self.radius = radius

        self.position = position
        self.velocity = velocity

        self.color = (randint(0, 255), randint(0, 255), randint(0, 255)) if color is None else color

        self.image = pg.Surface((radius*2, radius*2))
        self.image.fill(bg_color)
        self.image.set_alpha(255)
        pg.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius, 0)

    def draw_on(self, screen):
        pg.draw.circle(screen, self.color, (int(self.position[0]), int(self.position[1])), self.radius, 0)

    def effect_of(self, other):
        M = other.mass
        x_distance = other.position[0]-self.position[0]
        y_distance = other.position[1] - self.position[1]
        # distance_ratio = float(x_distance) / float(y_distance)
        r = (x_distance**2 + y_distance**2) ** 0.5
        angle = atan2(y_distance, x_distance)
        magnitude = (G * M) / (r ** 2)
        x_accel = magnitude * cos(angle)
        y_accel = magnitude * sin(angle)
        # set a ceiling on body acceleration
        x_accel = min(x_accel, 100)
        y_accel = min(y_accel, 100)

        return (x_accel , y_accel)

    def test_collision(self, other):
        return (abs(other.position[0] - self.position[0]) ** 2 + abs(other.position[1] - self.position[1]) ** 2) ** 0.5 < (self.radius + other.radius) * 0.5        #'...) * 0.5' gives collosion tolerance equal to the mean radius

    def merge(self, other):
        # print "merge!"
        self.position[0] = (self.position[0]*self.mass + other.position[0]*other.mass) / (self.mass + other.mass)
        self.position[1] = (self.position[1] * self.mass + other.position[1] * other.mass) / (self.mass + other.mass)

        self.velocity[0] = (self.velocity[0]*self.mass + other.velocity[0]*other.mass) / (self.mass + other.mass)
        self.velocity[1] = (self.velocity[1] * self.mass + other.velocity[1] * other.mass) / (self.mass + other.mass)

        self.radius = max(self.radius, other.radius) * (float(self.mass + other.mass) / self.mass) ** 0.3333333
        self.radius = int(self.radius)

        self.color = ((self.color[0]*self.mass + other.color[0]*other.mass)/(self.mass + other.mass),
                      (self.color[1]*self.mass + other.color[1]*other.mass)/(self.mass + other.mass),
                      (self.color[2]*self.mass + other.color[2]*other.mass)/(self.mass + other.mass))

        self.mass += other.mass

    def apply_acceleration(self, acceleration):
        self.velocity[0] += acceleration[0]
        self.velocity[1] += acceleration[1]

    def apply_velocity(self):
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
