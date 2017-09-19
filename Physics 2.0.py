from functools import reduce
from operator import add
from random import shuffle
from pygame.math import Vector2 as V2
import pygame as pg

from src.display.tkinter_windows import *
from src.core.presets import System, Gradient
from src.core import constants

# Import Structure
# Constants -> Bodies -> Presets --(+JsonSaving)--> TkinterWindows -> Physics 2.0

def display(settings_window, screen, bodies, cam):
    screen.fill(settings_window.bg_color)  # comment out this line for a fun time ;)
    if settings_window.walls.get():
        pg.draw.rect(screen, (0, 0, 0), pg.Rect(0, 0, *cam.dims), 3)
    for b in bodies:
        # Calculate coordinates and radius adjusted for camera
        x, y = (b.position - cam.position - cam.dims / 2) * cam.scale + cam.dims / 2
        pg.draw.circle(screen, b.color, (int(x), int(y)), int(b.radius * cam.scale), 0)
    pg.display.update()


class Camera:
    def __init__(self, dims):
        self.position, self.velocity, self.dims, self.scale = V2(0, 0), V2(0, 0), dims, 1

    def move_to_com(self, bodies):
        total_mass = sum(b.mass for b in bodies)
        self.position = reduce(add, (b.position * b.mass for b in bodies)) / total_mass - self.dims / 2

    def move_to_body(self, body):
        self.position = body.position - self.dims / 2

    def apply_velocity(self):
        self.position += self.velocity


def main():
    pg.init()
    info = pg.display.Info()
    width, height = int(info.current_w * 0.6), int(info.current_h * 0.75)
    dims = V2(width, height)

    # Initialize camera object
    camera = Camera(dims)

    # Construct bodies list
    # bodies = System(dims, 100, (1,10), (75,500)).preset("unary", 5000, 0.3)
    # bodies = System(dims, 50, (10,15), (450,500)).preset("binary", (5000, 2500), 0.4)
    # bodies = System(dims, 100, (10,20), (5,500)).preset("cluster")
    # bodies = [Body(200, (400, 300), (1, 0), 0.01, (0,0,0), "A"), Body(100, (900, 330), (-1, 0), 0.01, (255, 255, 0), "B")]
    # bodies = Gradient(dims, 120, (500,1000)).preset("diffusion")
    bodies = Gradient(dims, 120, (500,1000)).preset("density", (0.1, 0.3))
    
    # Eliminates patterns that come from constant computation order
    shuffle(bodies)

    # Initialize settings window and clock
    settings_window, clock = Settings(bodies, camera, dims, [constants.G, constants.COR]), pg.time.Clock()

    # Center display in monitor
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    # Initialize screen
    icon = pg.image.load('AtomIcon.png')
    pg.display.set_icon(icon)
    screen = pg.display.set_mode((width, height), pg.RESIZABLE)
    pg.display.set_caption("Physics Simulator 2.0")

    Scroll, scroll_k, scroll_k2, scroll_down, scroll_scale = V2(0, 0), [pg.K_a, pg.K_w, pg.K_d, pg.K_s], [pg.K_RIGHT, pg.K_LEFT, pg.K_UP, pg.K_DOWN], [0, 0, 0, 0], 1

    # Initialize simulation sentinel and frame counter
    done = False
    frame_count = 0
    while not done:
        clock.tick(constants.clock_speed)
        frame_count += 1

        if settings_window.alive:
            settings_window.update()
            try: G, time_factor, COR, collision = settings_window.gravity_slider.get() / 100, settings_window.time_slider.get() / 100, settings_window.COR_slider.get(), settings_window.collision.get()
            except: pass

        for window in settings_window.properties_windows:
            if window.alive:
                window.update()
            else:
                settings_window.properties_windows.remove(window)

        for event in pg.event.get():
            if event.type == pg.VIDEORESIZE:
                width, height = event.w, event.h
                dims, screen = V2(width, height), pg.display.set_mode((width, height), pg.RESIZABLE)
            elif event.type == pg.KEYDOWN:
                if event.key in scroll_k:
                    scroll_down[scroll_k.index(event.key)] = 1
                elif event.key in scroll_k2:
                    camera.velocity += V2((3/camera.scale,0) if event.key in scroll_k2[:2] else (0,3/camera.scale)).elementwise() * ((scroll_k2.index(event.key) not in (1,2)) * 2 - 1)
            elif event.type == pg.KEYUP:
                if event.key in scroll_k:
                    scroll_down[scroll_k.index(event.key)] = 0
                elif event.key in scroll_k2:
                    camera.velocity = camera.velocity.elementwise() * ((0,1) if event.key in scroll_k2[:2] else (1,0))
            elif event.type == pg.QUIT:
                done = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pos = camera.position + (pg.mouse.get_pos() - dims / 2) / camera.scale + dims / 2
                    for b in bodies:
                        if b.click_collision(pos) and b not in [win.body for win in settings_window.properties_windows]:
                            if not settings_window.alive: # Respawn the main window if it is dead
                                settings_window = Settings(bodies, camera, dims, [constants.G, constants.COR]) # This still does not fix all errors, and all settings are reset to defaults
                            settings_window.properties_windows.append(BodyProperties(bodies, camera, dims, len(settings_window.properties_windows), b))
                elif event.button == 4:
                    camera.scale = min(camera.scale * 1.1, 100)
                    scroll_scale /= 1.1
                elif event.button == 5:
                    camera.scale = max(camera.scale / 1.1, 0.01)
                    scroll_scale *= 1.1

        # Apply velocity to camera
        camera.apply_velocity()

        # Reset accelerations
        for b in bodies:
            b.acceleration = V2(0, 0)  # Reset to 0 (to ignore previous clock tick's calculations)

        # Calculate forces and set acceleration, if mutual gravitation is enabled
        for b in range(len(bodies)):
            for o in range(len(bodies) - 1, b, -1):
                if collision and bodies[o].test_collision(bodies[b]):
                    bodies[o].collide(bodies[b], COR, settings_window.properties_windows)
                    if COR == 0: # Only remove second body if collision is perfectly inelastic
                        bodies.pop(b)
                        break
                if settings_window.gravity_on.get():
                        force = bodies[b].force_of(bodies[o], G)
                        bodies[b].acceleration += bodies[o].mass * force
                        bodies[o].acceleration += -bodies[b].mass * force

        # Uniform Gravitational field if option is enabled
        if settings_window.g_field.get():
            for b in bodies:
                b.acceleration.y += G / 50

        # Display current frame
        display(settings_window, screen, bodies, camera)

        # Apply acceleration and velocity
        for body in bodies:
            body.apply_motion(time_factor)
            body.position += Scroll

        # Wall collision
        if settings_window.walls.get():
            for b in bodies:
                d, r = ((b.position - camera.position) - dims / 2) * camera.scale + dims / 2, b.radius * camera.scale
                for i in 0, 1:
                    x = d[i] # x is the dimension (x,y) currently being tested / edited
                    if x <= r or x >= dims[i] - r:
                        b.velocity[i] *= -COR # Reflect the perpendicular velocity
                        b.position[i] = (2*(x<r)-1) * (r-dims[i]/2) / camera.scale + dims[i] / 2 + camera.position[i] # Place body back into frame
                
        # Kill a body if too far from origin (only check every 100 ticks)
        if frame_count % 100 == 0:
            for b in bodies:
                if b.position.length() > 100000:  # TODO: find a good value from this boundary
                    bodies.remove(b)

        # Update scrolling
        Scroll = (Scroll + scroll_scale * (V2(scroll_down[:2])-scroll_down[2:])) * .95

    pg.quit()
    if settings_window.alive: settings_window.destroy()


if __name__ == "__main__":
    main()
