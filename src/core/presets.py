from .bodies import *

class Preset:
    def __init__(self, dims, num, mass_range, *args):
        self.num, (self.width, self.height), self.m_range = num, dims, mass_range
        self.extra_args(*args)

    def preset(self, preset_type, *args):
        return generate_bodies(getattr(self, preset_type)(*args))

class Gradient(Preset):
    def extra_args(self, colors=((255, 0, 0), (0, 0, 255))):
        self.colors = colors

    def Diffusion(self):
        return [(uniform(*self.m_range), (uniform(self.width * y/2, self.width * (y+1)/2-1), uniform(0, self.height)), (uniform(-1, 1), uniform(-1, 1)), Density, self.colors[y]) for _ in range(self.num//2) for y in (0,1)]

    def Density(self, densities):
        return [(uniform(*self.m_range), (uniform(0, self.width), uniform(0, self.height)), (uniform(-1, 1), uniform(-1, 1)), densities[y], self.colors[y]) for _ in range(self.num//2) for y in (0,1)]


class System(Preset):
    def extra_args(self, dist_range, planet_density=Density):
        self.d_range, self.density = dist_range, planet_density

    def Cluster(self):
        bodies = []
        for x in range(self.num):
            mass, distance, angle = uniform(*self.m_range), uniform(*self.d_range), uniform(-pi, pi)
            position = (self.width/2 + distance * cos(angle), self.height/2 - distance * sin(angle))
            velocity = (uniform(-2, 2), uniform(-2, 2))
            bodies.append((mass, position, velocity, self.density, None, "Planet " + str(x)))
        return bodies

    def Unary(self, star_mass, star_density, circular=True):
        bodies = [(star_mass, (self.width/2, self.height/2),  (0, 0), star_density, (255, 255, 0), "Star")]
        for x in range(self.num):
            mass = uniform(*self.m_range)
            distance = uniform(*self.d_range)
            angle = uniform(-pi, pi)
            position = (self.width/2 + distance * cos(angle), self.height/2 - distance * sin(angle))
            if circular:
                speed = sqrt(star_mass * G / distance)
                velocity = (speed * sin(angle), speed * cos(angle))
            else:
                velocity = (uniform(-2, 2), uniform(-2, 2))
            bodies.append((mass, position, velocity, self.density, None, "Planet " + str(x)))
        return bodies

    def Binary(self, star_masses, star_density):
        stars, distance = [[m, [0,0], [0,0], star_density] for m in star_masses], uniform(*self.d_range)
        for s in 0, 1:
            stars[s][1] = V2(self.width/2 + (-4 if s else 4) * (star_masses[s]/star_density)**(1/3), self.height/2)
            stars[s][2] = V2(0, (1 - 2*s) * sqrt(G * star_masses[1-s] / distance))
        return stars + [((uniform(*self.m_range), (self.width/2 + uniform(-distance, distance), self.height/2 + uniform(-distance, distance)), (uniform(-1, 1), uniform(-1, 1)), self.density)) for _ in range(self.num)]
