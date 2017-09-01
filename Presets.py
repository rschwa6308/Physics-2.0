from random import uniform
from math import pi, sin, cos, sqrt

from Bodies import *
from Colors import *


def cluster(planets, min_mass, max_mass, min_distance, max_distance, circular=True, planet_density=Density):
    bodies = []

    total_mass = 0
    for x in range(planets):
        mass = uniform(min_mass, max_mass)
        total_mass += mass
        distance = uniform(min_distance, max_distance)
        angle = uniform(-1*pi, pi)
        position = V2(width/2 + distance * cos(angle), height/2 - distance * sin(angle))
        if circular:
            speed = sqrt(total_mass * G / distance)
            velocity = V2(speed * sin(angle), speed * cos(angle))
        else:
            velocity = V2(uniform(-2, 2), uniform(-2, 2))
        planet = Body(mass, position, velocity, density=planet_density, name="planet " + str(x))
        bodies.append(planet)

    return bodies


def star_system(star_mass, star_density, planets, min_mass, max_mass, min_distance, max_distance, circular=True, planet_density=Density):
    bodies = []

    star = Body(star_mass, [width/2, height/2], [0, 0], star_density, yellow, "Star")
    bodies.append(star)

    for x in range(planets):
        mass = uniform(min_mass, max_mass)
        distance = uniform(min_distance, max_distance)
        angle = uniform(-1*pi, pi)
        position = V2(star.position[0] + distance * cos(angle), star.position[1] - distance * sin(angle))
        if circular:
            speed = sqrt(star_mass * G / distance)
            velocity = V2(speed * sin(angle), speed * cos(angle))
        else:
            velocity = V2(uniform(-2, 2), uniform(-2, 2))
        planet = Body(mass, position, velocity, density=planet_density, name="planet " + str(x))
        bodies.append(planet)

    return bodies


def binary_system(star_mass_a, star_mass_b, planets, min_mass, max_mass):
    bodies = []

    star_a = Body(star_mass_a, [0, 0], [0, 0], density=0.04)
    star_b = Body(star_mass_a, [0, 0], [0, 0], density=0.04)

    star_a.position = V2([width/2 - 4*star_a.radius, height/2])
    star_b.position = V2([width/2 + 4*star_b.radius, height/2])

    distance = abs(star_b.position[0] - star_a.position[0])

    star_a.velocity = V2([0, sqrt(G * star_mass_b / distance)])
    star_b.velocity = V2([0, -1 * sqrt(G * star_mass_a / distance)])

    bodies.extend([star_a, star_b])

    # planets_list = [Body(uniform(min_mass, max_mass), [width/2 + uniform(-3 * distance, 3 * distance), height/2 + uniform(-3 * distance, 3 * distance)], [uniform(-1, 1), uniform(-1, 1)]) for _ in range(planets)]
    # bodies.extend(planets_list)
    for _ in range(planets):
        mass = uniform(min_mass, max_mass)
        position = [width/2 + uniform(-3 * distance, 3 * distance), height/2 + uniform(-3 * distance, 3 * distance)]
        velocity = [uniform(-1, 1), uniform(-1, 1)]

        planet = Body(mass, position, velocity)
        bodies.append(planet)

    return bodies
