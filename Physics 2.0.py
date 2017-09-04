from functools import reduce
from operator import add

from Presets import *
from TkinterWindows import *


def display(settings_window, screen, bodies, cam):
    # Clear last frame
    screen.fill(settings_window.bg_color)  # comment out this line for a fun time ;)
    # Draw walls if on
    if settings_window.walls.get():
        pg.draw.rect(screen, (0, 0, 0), pg.Rect(0, 0, width, height), 3)
    # Display all bodies
    for b in bodies:
        # calculate coordinates and radius adjusted for camera
        x = b.position[0] - cam.position[0]
        x = (x - width / 2) * cam.scale + width / 2
        y = b.position[1] - cam.position[1]
        y = (y - height / 2) * cam.scale + height / 2
        radius = b.radius * cam.scale
        pg.draw.circle(screen, b.color, (int(x), int(y)), int(radius), 0)
    pg.display.update()


class Camera:
    def __init__(self, position=None, scale=None):
        self.position = V2(0, 0)
        self.velocity = V2(0, 0)
        self.scale = 1

    def move_to_com(self, bodies):
        total_mass = sum(b.mass for b in bodies)
        self.position = reduce(add, (b.position * b.mass for b in bodies)) / total_mass - V2(width, height) / 2

    def move_to_body(self, body):
        x, y = body.position
        x -= width / 2
        y -= height / 2
        self.position = V2(x, y)

    def apply_velocity(self):
        self.position += self.velocity


def main():
    global width, height

    # Initialize pygame
    pg.init()

    # Initialize camera object
    camera = Camera()

    # Construct bodies list
    #                   (star_mass, star_density, planets, min_mass, max_mass, min_distance, max_distance)
    # bodies = star_system(5000, 0.1, 100, 1, 10, 75, 500, planet_density=0.4)
    # bodies = binary_system(1000, 800, 150, 2, 10)
    # bodies = cluster(50, 10, 10, 10, 100, False)
    # bodies = cluster(100, 10, 20, 5, 500, False)
    bodies = [Body(200, (200, 200), (1, 0), 0.01, (0,0,0), "A"), Body(100, (500, 230), (-1, 0), 0.01, (255,255,0), "B")]

    # Initialize settings window
    settings_window = Settings(bodies, camera)

    # Initialize body properties window list
    properties_windows = []

    # Initialize collision setting to True
    collision = 1

    # Initialize body count
    settings_window.set_bodies(len(bodies))

    # Center display in monitor
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    # Initialize screen
    icon = pg.image.load('AtomIcon.png')
    pg.display.set_icon(icon)
    screen = pg.display.set_mode((width, height), pg.RESIZABLE)
    pg.display.set_caption("Physics Simulator 2.0")

    # Initialize simulation clock and time factor
    clock = pg.time.Clock()
    time_factor = 1

    scroll = V2(0, 0)
    scroll_keys = [pg.K_d, pg.K_a, pg.K_w, pg.K_s]
    scrolling = [0, 0, 0, 0]
    scroll_constant = 1

    # Initialize simulation sentinel and frame counter
    done = False
    frame_count = 0
    while not done:
        clock.tick(clock_speed)
        frame_count += 1

        if settings_window.alive:
            settings_window.update()
            G = settings_window.get_gravity()
            time_factor = settings_window.get_time()
            COR = settings_window.get_COR()
            collision = settings_window.get_collision()

        for window in properties_windows:
            if window.alive:
                window.update()
            else:
                properties_windows.remove(window)

        for event in pg.event.get():
            if event.type == pg.VIDEORESIZE:
                width, height = event.w, event.h
                screen = pg.display.set_mode((width, height), pg.RESIZABLE)
            elif event.type == pg.KEYDOWN:
                if event.key in scroll_keys:
                    scrolling[scroll_keys.index(event.key)] = 1
                elif event.key == pg.K_LEFT:
                    camera.velocity[0] = -3 / camera.scale
                elif event.key == pg.K_RIGHT:
                    camera.velocity[0] = 3 / camera.scale
                elif event.key == pg.K_UP:
                    camera.velocity[1] = -3 / camera.scale
                elif event.key == pg.K_DOWN:
                    camera.velocity[1] = 3 / camera.scale
            elif event.type == pg.KEYUP:
                if event.key in scroll_keys:
                    scrolling[scroll_keys.index(event.key)] = 0
                elif event.key == pg.K_LEFT:
                    camera.velocity[0] = 0
                elif event.key == pg.K_RIGHT:
                    camera.velocity[0] = 0
                elif event.key == pg.K_UP:
                    camera.velocity[1] = 0
                elif event.key == pg.K_DOWN:
                    camera.velocity[1] = 0
            elif event.type == pg.QUIT:
                done = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x, y = pg.mouse.get_pos()
                    x = camera.position[0] + (x - width / 2) / camera.scale + width / 2
                    y = camera.position[1] + (y - height / 2) / camera.scale + height / 2
                    for b in bodies:
                        if b.click_collision((x, y)):
                            if b not in [win.body for win in properties_windows]:
                                properties_windows.append(BodyProperties(b, bodies, len(properties_windows), camera))

                elif event.button == 4:
                    camera.scale *= 1.1
                    camera.scale = min(camera.scale, 100)
                    scroll_constant /= 1.1
                elif event.button == 5:
                    camera.scale /= 1.1
                    camera.scale = max(float(camera.scale), 0.01)
                    scroll_constant *= 1.1

        # Apply velocity to camera
        camera.apply_velocity()

        # Reset accelerations
        for b in bodies:
            b.acceleration = V2(0, 0)  # Reset to 0 (to ignore previous clock tick's calculations)

        # Calculate forces and set acceleration
        for b in range(len(bodies)):
            for o in range(len(bodies) - 1, b, -1):
                if collision and bodies[b].test_collision(bodies[o]):
                    bodies[b].collide(bodies[o], COR, properties_windows)
                    if COR == 0:            # Only remove second body if collision is perfectly inelastic
                        bodies.pop(o)
                else:
                    force = bodies[b].force_of(bodies[o], G)
                    bodies[b].acceleration += bodies[o].mass * force
                    bodies[o].acceleration += -bodies[b].mass * force

        # Apply acceleration
        for b in bodies:
            b.apply_acceleration(time_factor)

        # Display current frame
        display(settings_window, screen, bodies, camera)

        # Apply velocity (update position)
        for body in bodies:
            body.apply_velocity(time_factor)
            body.position += scroll

        # TEMPORARY wall collision (for the lols)
        if settings_window.walls.get():
            for b in bodies:
                x = b.position[0] - camera.position[0]
                x = (x - width / 2) * camera.scale + width / 2
                y = b.position[1] - camera.position[1]
                y = (y - height / 2) * camera.scale + height / 2
                radius = b.radius * camera.scale
                if x - radius < 0:
                    b.position.x = ((radius) - width / 2) / camera.scale + width / 2
                    b.velocity.x *= -1
                elif x + radius > width:
                    b.position.x = ((width - radius) - width / 2) / camera.scale + width / 2
                    b.velocity.x *= -1
                if y - radius < 0:
                    b.position.y = ((radius) - height / 2) / camera.scale + height / 2
                    b.velocity.y *= -1
                elif y + radius > height:
                    b.position.y = ((height - radius) - height / 2) / camera.scale + height / 2
                    b.velocity.y *= -1

        # Kill a body if too far from origin (only check every 100 ticks)
        if frame_count % 100 == 0:
            for b in bodies:
                if max(b.position[0], b.position[1]) > 100000:  # TODO: find a good value from this boundary
                    bodies.remove(b)

        # Accelerate scrolling
        if scrolling[0]:
            scroll[0] -= scroll_constant
        if scrolling[1]:
            scroll[0] += scroll_constant
        if scrolling[2]:
            scroll[1] += scroll_constant
        if scrolling[3]:
            scroll[1] -= scroll_constant

        # Decelerate scrolling
        scroll *= .95

    pg.quit()
    if settings_window.alive: settings_window.destroy()


if __name__ == "__main__":
    main()
