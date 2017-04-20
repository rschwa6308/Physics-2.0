import tkinter as tk
import os
from functools import reduce
from operator import add

from Presets import *
from Constants import *



class Settings:
    def __init__(self, bodies, camera):
        self.bodies = bodies
        self.camera = camera

        self.root = tk.Tk()
        self.root.title("Universe Settings")

        self.root.protocol("WM_DELETE_WINDOW", self.destroy)
        self.alive = True

        tk.Label(self.root, text="Gravity: ").grid(row=0)
        self.gravity_slider = tk.Scale(self.root, from_=0, to = 1000, orient=tk.HORIZONTAL, length=200)
        self.gravity_slider.set(G*100)
        self.gravity_slider.grid(row=0, column=1)

        tk.Label(self.root, text="Time Factor (%): ").grid(row=1, sticky=tk.E)
        self.time_slider = tk.Scale(self.root, from_=-0, to=500, orient=tk.HORIZONTAL, length=200)      # from_ can be set negative for rewind
        self.time_slider.set(100)
        self.time_slider.grid(row=1, column=1)

        self.bodies_label_text = tk.StringVar()
        self.bodies_label = tk.Label(self.root, textvariable=self.bodies_label_text)
        self.bodies_label.grid(row=2, column=0, pady=5)

        self.merge = tk.IntVar()
        self.merge.set(1)
        self.merge_checkbutton = tk.Checkbutton(self.root, text="Merges", variable=self.merge)
        self.merge_checkbutton.grid(row=2, column=1, pady=5, sticky=tk.W)

        tk.Button(self.root, text="Move Cam to COM", command=self.center_cam).grid(row=3, column=0)

        tk.Button(self.root, text="Quit", command=self.quit).grid(row=4, column=0, rowspan=2, columnspan=2, pady = 20)

        self.root.geometry('%dx%d+%d+%d' % (320, 200, monitor_width/2 - width/2 - 330, monitor_height/2 - height/2 - 20))

    def get_gravity(self):
        try:
            return self.gravity_slider.get() / 100.0
        except:
            return G

    def get_time(self):
        try:
            return self.time_slider.get() / 100.0
        except:
            return 1

    def get_merge(self):
        return self.merge.get()
        
    def set_bodies(self, n):
        self.bodies_label_text.set("Bodies: " + str(n))

    def center_cam(self):
        self.camera.move_to_com(self.bodies)

    def quit(self):
        pg.quit()
        self.destroy()

    def update(self):
        self.root.update()

    def destroy(self):
        self.alive = False
        self.root.destroy()


class BodyProperties:
    def __init__(self, body, queue_position, camera):
        self.camera = camera

        self.original = body.copy()
        self.body = body

        self.root = tk.Tk()
        self.root.title(self.body.name if self.body.name is not None else "Unnamed Body")

        self.root.protocol("WM_DELETE_WINDOW", self.destroy)
        self.alive = True

        tk.Label(self.root, text="Mass (%): ").grid(row=1)
        self.mass_slider = tk.Scale(self.root, from_=1, to=1000, orient=tk.HORIZONTAL, length=100)
        self.mass_slider.set(100)
        self.mass_slider.grid(row=1, column=1)

        tk.Label(self.root, text="Density (%): ").grid(row=2)
        self.density_slider = tk.Scale(self.root, from_=10, to=1000, orient=tk.HORIZONTAL, length=100)
        self.density_slider.set(100)
        self.density_slider.grid(row=2, column=1)

        tk.Button(self.root, text="Focus", command=self.focus).grid(row=3)          # TODO: change button text?

        self.canvas = tk.Canvas(self.root, width=104, height=104)
        self.update_canvas()

        self.width = 220
        self.height = 250
        self.root.geometry('%dx%d+%d+%d' % (self.width, self.height, monitor_width / 2 - width / 2 - 10 - self.width, monitor_height / 2 - 330 + (self.height + 31) * (queue_position)))

    def focus(self):
        self.camera.move_to_body(self.body)

    def update_canvas(self):
        self.canvas.delete("all")
        self.canvas.create_oval((2, 2, 102, 102))
        self.canvas.create_line((52, 2, 52, 102), fill="Dark Gray", dash=(2, 2))
        self.canvas.create_line((2, 52, 102, 52), fill="Dark Gray", dash=(2, 2))

        mag_vel = abs(hypot(self.body.velocity[0], self.body.velocity[1]))
        scale_factor = 40 * (1 - 2 ** -mag_vel) / mag_vel  if mag_vel != 0 else 0
        x_vel, y_vel = [scale_factor * self.body.velocity[n] for n in (0, 1)]
        self.canvas.create_line((52, 52, 52 + x_vel, 52 + y_vel), fill="Blue", arrow="last")

        mag_acc = abs(hypot(self.body.acceleration[0], self.body.acceleration[1]))
        scale_factor = 40 * (1 - 2 ** -(mag_acc*1000000)) / mag_acc if mag_acc != 0 else 0
        x_acc, y_acc = [scale_factor * self.body.acceleration[n] for n in (0, 1)]
        self.canvas.create_line((52, 52, 52 + x_acc, 52 + y_acc), fill="Red", arrow="last")

        self.canvas.grid(row=4, columnspan=4)

    def update(self):
        self.root.update()
        self.body.mass = self.original.mass * (self.mass_slider.get() / 100.0)
        self.body.density = self.original.density * (self.density_slider.get() / 100.0)
        self.body.update_radius()
        self.update_canvas()

    def destroy(self):
        self.root.destroy()
        self.alive = False


def display(screen, bodies, cam):
    # Clear last frame
    screen.fill(bg_color)           # comment out this line for a fun time ;)
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
    def __init__(self):
        self.position = V2(0, 0)
        self.velocity = V2(0, 0)
        self.scale = 1

    def move_to_com(self, bodies):
        total_mass = sum(b.mass for b in bodies)
        self.position = reduce(add,(b.position * b.mass for b in bodies)) / total_mass - V2(width,height) / 2

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
    bodies = star_system(5000, 0.1, 100, 1, 10, 75, 500, planet_density=0.4)
    # bodies = binary_system(1000, 800, 150, 2, 10)

    # Initialize settings window
    settings_window = Settings(bodies, camera)

    # Initialize body properties window list
    properties_windows = []

    # Initialize merge setting to True
    merge = 1

    # Initialize body count
    settings_window.set_bodies(len(bodies))

    # Center display in monitor
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    
    # Initialize screen
    icon = pg.image.load('AtomIcon.png')
    pg.display.set_icon(icon)
    screen = pg.display.set_mode((width, height), pg.RESIZABLE)
    pg.display.set_caption("Physics Simulator 2")

    # Initialize simulation clock and time factor
    clock = pg.time.Clock()
    time_factor = 1

    scroll = V2(0,0)
    scroll_right, scroll_left, scroll_down, scroll_up = 0, 0, 0, 0
    scroll_constant = 2.5

    # Initialize simulation sentinel
    done = False
    while not done:
        clock.tick(clock_speed)

        if settings_window.alive:
            settings_window.update()
            G = settings_window.get_gravity()
            time_factor = settings_window.get_time()
            merge = settings_window.get_merge()

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
                if event.key == pg.K_d:
                    scroll_right = 1 
                elif event.key == pg.K_a:
                    scroll_left = 1
                elif event.key == pg.K_w:
                    scroll_up = 1
                elif event.key == pg.K_s:
                    scroll_down = 1
                elif event.key == pg.K_LEFT:
                    camera.velocity[0] = -3 / camera.scale
                elif event.key == pg.K_RIGHT:
                    camera.velocity[0] = 3  / camera.scale
                elif event.key == pg.K_UP:
                    camera.velocity[1] = -3 / camera.scale
                elif event.key == pg.K_DOWN:
                    camera.velocity[1] = 3 / camera.scale
            elif event.type == pg.KEYUP:
                if event.key == pg.K_d:
                    scroll_right = 0
                elif event.key == pg.K_a:
                    scroll_left = 0
                elif event.key == pg.K_w:
                    scroll_up = 0
                elif event.key == pg.K_s:
                    scroll_down = 0
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
                                properties_windows.append(BodyProperties(b, len(properties_windows), camera))

                elif event.button == 4:
                    camera.scale *= 1.1
                    camera.scale = min(camera.scale, 100)
                elif event.button == 5:
                    camera.scale /= 1.1
                    camera.scale = max(float(camera.scale), 0.01)

        # Apply velocity to camera
        camera.apply_velocity()

        # Reset accelerations
        for b in bodies:
            b.acceleration = V2(0, 0)  # Reset to 0 (to ignore previous clock tick's calculations)

        # Calculate forces and set acceleration
        for b in range(len(bodies)):
            for o in range(len(bodies)-1,b,-1):
                if merge and bodies[b].test_collision(bodies[o]):           # Merge setting check must precede collision check for optimization purposes (https://docs.python.org/3/library/stdtypes.html#boolean-operations-and-or-not)
                    bodies[b].merge(bodies[o], properties_windows)
                    bodies.pop(o)
                    if settings_window.alive:
                        settings_window.set_bodies(len(bodies))
                else:
                    force = bodies[b].force_of(bodies[o], G)
                    bodies[b].acceleration += bodies[o].mass * force
                    bodies[o].acceleration += -bodies[b].mass * force

        # Apply acceleration
        for b in bodies:
            b.apply_acceleration(time_factor)


        # Display current frame
        display(screen, bodies, camera)
        
        # Apply velocity (update position)
        for body in bodies:
            body.apply_velocity(time_factor)
            body.position += scroll

        # Accelerate scrolling
        if scroll_right:
            scroll[0] -= scroll_constant
        if scroll_left:
            scroll[0] += scroll_constant
        if scroll_up:
            scroll[1] += scroll_constant    
        if scroll_down:
            scroll[1] -= scroll_constant
        # Decelerate scrolling
        if scroll[0]:
            scroll[0] -= abs(scroll[0])/scroll[0]
        if scroll[1]:
            scroll[1] -= abs(scroll[1])/scroll[1]

    pg.quit()
    if settings_window.alive: settings_window.destroy()



if __name__ == "__main__":
    main()
