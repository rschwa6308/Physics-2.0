from random import uniform
from math import pi

from Bodies import *


def star_system(star_mass, star_density, planets, min_mass, max_mass, min_distance, max_distance, circular=True):
    bodies = []

    star = Body(star_mass, [width/2, height/2], [0, 0], star_density, yellow)
    bodies.append(star)

    for x in range(planets):
        mass = uniform(min_mass, max_mass)
        distance = uniform(min_distance, max_distance)
        angle = uniform(-1*pi, pi)
        position = [star.position[0] + distance * cos(angle), star.position[1] - distance * sin(angle)]
        if circular:
            acceleration_c = (star_mass * G)/(distance ** 2)
            speed = (acceleration_c * distance) ** 0.5
            velocity = [speed * sin(angle), speed * cos(angle)]
        else:
            velocity = [uniform(-2, 2), uniform(-2, 2)]
        planet = Body(mass, position, velocity)
        bodies.append(planet)


    return bodies
