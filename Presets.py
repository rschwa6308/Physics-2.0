from Bodies import *

def cluster(planets, mass_range, dist_range, circular=True, planet_density=Density):
    bodies = []
    total_mass = 0
    for x in range(planets):
        mass = uniform(*mass_range)
        total_mass += mass
        distance = uniform(*dist_range)
        angle = uniform(-pi, pi)
        position = (width/2 + distance * cos(angle), height/2 - distance * sin(angle))
        if circular:
            speed = sqrt(total_mass * G / distance)
            velocity = (speed * sin(angle), speed * cos(angle))
        else:
            velocity = (uniform(-2, 2), uniform(-2, 2))
        planet = Body(mass, position, velocity, density=planet_density, name="planet " + str(x))
        bodies.append(planet)
    return bodies


def diffusion_gradient(num, mass, colors):
    bodies = []
    for x in range(num // 2):
        for y in 0, 1:
            bodies.append(Body(mass, ((uniform(width / 2 + 1, width) if y else uniform(0, width / 2 - 1)), uniform(0, height)), (uniform(-1, 1), uniform(-1, 1)), color=colors[y]))
    return bodies


def density_gradient(num, mass_range, densities, colors):
    bodies = []
    for x in range(num // 2):
        for y in 0, 1:
            bodies.append(Body(uniform(*mass_range), (uniform(0, width), uniform(0, height)), (uniform(-1, 1), uniform(-1, 1)), density=densities[y], color=colors[y]))
    return bodies


def star_system(star_mass, star_density, planets, mass_range, dist_range, circular=True, planet_density=Density):
    bodies = []
    star = Body(star_mass, (width/2, height/2),  (0, 0), star_density, (255, 255, 0), "Star")
    bodies.append(star)
    for x in range(planets):
        mass = uniform(*mass_range)
        distance = uniform(*dist_range)
        angle = uniform(-pi, pi)
        position = (star.position[0] + distance * cos(angle), star.position[1] - distance * sin(angle))
        if circular:
            speed = sqrt(star_mass * G / distance)
            velocity = (speed * sin(angle), speed * cos(angle))
        else:
            velocity = (uniform(-2, 2), uniform(-2, 2))
        planet = Body(mass, position, velocity, density=planet_density, name="planet " + str(x))
        bodies.append(planet)
    return bodies


def binary_system(star_masses, star_density, planets, mass_range, planet_density=Density):
    bodies = []
    stars = [Body(m, [0,0], [0,0], star_density) for m in star_masses]
    for s in 0, 1:
        stars[s].position = V2(width/2 + (-4 if s else 4) * stars[s].radius, height/2)
    distance = (stars[0].position - stars[1].position)[0] * 3
    for s in 0, 1:
        stars[s].velocity = V2(0, (-1 if s else 1) * sqrt(G * stars[1-s].mass / distance))
    bodies += stars
    for _ in range(planets):
        mass = uniform(*mass_range)
        position = (width/2 + uniform(-distance, distance), height/2 + uniform(-distance, distance))
        velocity = (uniform(-1, 1), uniform(-1, 1))
        planet = Body(mass, position, velocity, planet_density)
        bodies.append(planet)
    return bodies
