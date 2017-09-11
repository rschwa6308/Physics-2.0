from Constants import *

class Body:
    def __init__(self, mass, position, velocity, density=Density, color=None, name=None):
        self.mass = mass
        self.radius = int((mass/density)**(1/3))

        self.position = V2(position)
        self.velocity = V2(velocity)
        self.acceleration = V2(0, 0)

        self.density = density

        self.color = color if color else tuple(randint(0, 255) for _ in '111')

        self.name = name

    def copy(self):
        return Body(self.mass, self.position, self.velocity, self.density, self.color, None if self.name is None else self.name + " copy")     # inheritance of 'name' for debugging purposes only

    def draw_on(self, screen):
        pg.draw.circle(screen, self.color, (int(self.position[0]), int(self.position[1])), int(self.radius), 0)

    def click_collision(self, mouse_pos):
        mouse_pos = V2(mouse_pos)
        return self.position.distance_to(mouse_pos) < self.radius

    def force_of(self, other, G):
        x, y = (other.position[a] - self.position[a] for a in (0,1))
        r = hypot(x,y)
        if r == 0: return V2(0, 0)
        acc = G/r**3
        return V2(acc * x, acc * y)

    def test_collision(self, other):
        return self.position.distance_to(other.position) < self.radius + other.radius # Zero-tolerance collision

    def collide(self, other, COR, prop_wins):
        m, m2, v, v2, x, x2 = self.mass, other.mass, self.velocity, other.velocity, self.position, other.position
        M = m + m2
        # Special case: perfectly inelastic collision results in merging of the two bodies
        if COR == 0:
            self.position = (x*m + x2*m2) / M
            self.velocity = (v*m + v2*m2) / M

            avg_density = (self.density * m + other.density * m2) / M
            self.radius = int((M/avg_density)**(1/3))
            self.color = tuple(((self.color[x]*m + other.color[x]*m2)/M) for x in (0,1,2))
            self.mass = M

            # Check to see if the deleted body belongs to a properties window; If so, set win.body to the combined body
            for win in prop_wins:
                if win.body is other:
                    win.body = self
        else:
            # Explanation can be found here --->        http://ericleong.me/research/circle-circle/
            if (x2 - x).length() == 0:
                return          # TODO: find better solution
            n = (x2 - x).normalize()
            p = 2 * (v.dot(n) - v2.dot(n)) / M
            # TODO: properly incorporate COR.  This is currently incorrect, and is only a proof of concept
            self.velocity = v - (p * m2 * n) * COR
            other.velocity = v2 + (p * m * n) * COR
            # Set position of bodies to outer boundary to prevent bodies from getting stuck together
            # this method of splitting the offset evenly works, but is imprecise.  It should be based off of velocity.
            offset = (self.radius + other.radius) - (x2 - x).length()
            offset_vector = n * offset
            self.position -= offset_vector / 2
            other.position += offset_vector / 2

    def update_radius(self):
        self.radius = int((self.mass / self.density) ** (1 / 3))

    def apply_acceleration(self, time_factor):
        self.velocity += self.acceleration * time_factor

    def apply_velocity(self, time_factor):
        self.position += self.velocity * time_factor
