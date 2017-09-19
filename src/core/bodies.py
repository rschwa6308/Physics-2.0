from .constants import *

class Body:
    def __init__(self, mass, position, velocity, density=Density, color=None, name=None):
        self.mass, self.density, self.radius, self.color, self.name = mass, density, int((mass/density)**(1/3)), color if color else tuple(randint(0, 255) for _ in '111'), name
        self.position, self.velocity, self.acceleration = V2(position), V2(velocity), V2(0, 0)

    def draw_on(self, screen):
        pg.draw.circle(screen, self.color, list(map(int, self.position)), int(self.radius), 0)

    def click_collision(self, mouse_pos):
        return self.position.distance_to(mouse_pos) < self.radius

    def force_of(self, other, G):
        d = other.position - self.position
        r = d.length()
        return G/r**3 * d if r else V2(0, 0)

    def test_collision(self, other):
        return self.position.distance_to(other.position) < self.radius + other.radius # Zero-tolerance collision

    def merge(self, other, prop_wins): # Special case: perfectly inelastic collision results in merging of the two bodies
        m, m2, v, v2, x, x2 = self.mass, other.mass, self.velocity, other.velocity, self.position, other.position; M = m + m2
        self.position, self.velocity, self.mass, self.radius, self.color = (x*m + x2*m2) / M,  (v*m + v2*m2) / M, M, int((M*M/(self.density * m + other.density * m2))**(1/3)), tuple(((self.color[x]*m + other.color[x]*m2)/M) for x in (0,1,2))
        # Check to see if the deleted body belongs to a properties window; If so, set win.body to the combined body
        for win in prop_wins:
            if win.body is other:
                win.body = self
                
    def collide(self, other, COR):
        m, m2, v, v2, x, x2 = self.mass, other.mass, self.velocity, other.velocity, self.position, other.position; M = m + m2
        # Explanation can be found at http://ericleong.me/research/circle-circle/
        if (x2 - x).length() == 0: return # Ignore bodies in the exact same position
        n = (x2 - x).normalize()
        p = 2 * (v.dot(n) - v2.dot(n)) / M
        # TODO: properly incorporate COR.  This is currently incorrect, and is only a proof of concept
        self.velocity, other.velocity = v - (p * m2 * n) * COR, v2 + (p * m * n) * COR
        # Set position of bodies to outer boundary to prevent bodies from getting stuck together
        # this method of splitting the offset evenly works, but is imprecise.  It should be based off of velocity.
        offset = (self.radius + other.radius - (x2 - x).length()) * n
        self.position -= offset / 2
        other.position += offset / 2

    def update_radius(self):
        self.radius = int((self.mass / self.density) ** (1 / 3))

    def apply_motion(self, time_factor):
        self.velocity += self.acceleration * time_factor
        self.position += self.velocity * time_factor

def generate_bodies(body_args_list):
    return list(map(lambda args2: Body(*args2), body_args_list))

