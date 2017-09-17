from .bodies import *

class Preset:
    def __init__(self, dims):
        self.width, self.height = dims
    
    def generate(self, preset_type, *args):
        return list(map(lambda args2: Body(*args2), getattr(self, preset_type)(*args)))

    def cluster(self, planets, mass_range, dist_range, circular=True, planet_density=Density):
        bodies = []
        total_mass = 0
        for x in range(planets):
            mass = uniform(*mass_range)
            total_mass += mass
            distance = uniform(*dist_range)
            angle = uniform(-pi, pi)
            position = (self.width/2 + distance * cos(angle), self.height/2 - distance * sin(angle))
            if circular:
                speed = sqrt(total_mass * G / distance)
                velocity = (speed * sin(angle), speed * cos(angle))
            else:
                velocity = (uniform(-2, 2), uniform(-2, 2))
            planet = (mass, position, velocity, planet_density, None, "Planet " + str(x))
            bodies.append(planet)
        return bodies

    def diffusion_gradient(self, num, mass, colors):
        return [(mass, (uniform(self.width * y/2, self.width * (y+1)/2-1), uniform(0, self.height)), (uniform(-1, 1), uniform(-1, 1)), Density, colors[y]) for _ in range(num//2) for y in (0,1)]

    def density_gradient(self, num, mass_range, densities, colors):
        return [(uniform(*mass_range), (uniform(0, self.width), uniform(0, self.height)), (uniform(-1, 1), uniform(-1, 1)), densities[y], colors[y]) for _ in range(num//2) for y in (0,1)]

    def star_system(self, star_mass, star_density, planets, mass_range, dist_range, circular=True, planet_density=Density):
        bodies = []
        bodies.append((star_mass, (self.width/2, self.height/2),  (0, 0), star_density, (255, 255, 0), "Star"))
        for x in range(planets):
            mass = uniform(*mass_range)
            distance = uniform(*dist_range)
            angle = uniform(-pi, pi)
            position = (self.width/2 + distance * cos(angle), self.height/2 - distance * sin(angle))
            if circular:
                speed = sqrt(star_mass * G / distance)
                velocity = (speed * sin(angle), speed * cos(angle))
            else:
                velocity = (uniform(-2, 2), uniform(-2, 2))
            bodies.append((mass, position, velocity, planet_density, None, "Planet " + str(x)))
        return bodies

    def binary_system(self, star_masses, star_density, planets, mass_range, planet_density=Density):
        bodies = []
        stars = [(m, [0,0], [0,0], star_density) for m in star_masses]
        for s in 0, 1:
            stars[s][1] = V2(self.width/2 + (-4 if s else 4) * (star_masses[s]/star_density)**(1/3), self.height/2)
        distance = (stars[0][1] - stars[1][1])[0] * 3
        for s in 0, 1:
            stars[s][2] = V2(0, (1 - 2*s) * sqrt(G * star_masses[1-s] / distance))
        bodies += stars
        for _ in range(planets):
            mass = uniform(*mass_range)
            position = (self.width/2 + uniform(-distance, distance), self.height/2 + uniform(-distance, distance))
            velocity = (uniform(-1, 1), uniform(-1, 1))
            planet = (mass, position, velocity, planet_density)
            bodies.append(planet)
        return bodies
