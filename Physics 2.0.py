import tkinter as tk
import os

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
        self.time_slider = tk.Scale(self.root, from_=-200, to=500, orient=tk.HORIZONTAL, length=200)
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


def display(screen, bodies, cam):
    # Clear last frame
    screen.fill(bg_color)           # comment out this line for a fun time ;)
    # Display all bodies
    for b in bodies:
        #screen.blit(b.image, b.position)
        # b.draw_on(screen)
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
        self.position = [0, 0]
        self.velocity = [0, 0]
        self.scale = 1

    def move_to_com(self, bodies):
        total_mass = sum(b.mass for b in bodies)
        x = sum(b.position[0] * b.mass for b in bodies) / total_mass - width / 2
        y = sum(b.position[1] * b.mass for b in bodies) / total_mass - height / 2
        self.position = [x, y]

    def apply_velocity(self):
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]


def main():
    global width, height

    # Initialize camera object
    camera = Camera()

    # Construct bodies list

##    bodies = [
##         Body(1000, [1000, 500], [1, 0]),
##         Body(1000, [60, 800], [0, -1]),
##         Body(1000, [500, 150], [0, 0])
##    ]
    #                   (star_mass, star_density, planets, min_mass, max_mass, min_distance, max_distance)
    bodies = star_system(5000, 0.1, 100, 1, 10, 75, 500, planet_density=0.4)
    # bodies = binary_system(1000, 800, 150, 2, 10)

    # Initialize tkinter window
    settings_window = Settings(bodies, camera)

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
                if event.button == 4:
                    camera.scale *= 1.1
                    camera.scale = min(camera.scale, 100)
                elif event.button == 5:
                    camera.scale /= 1.1
                    camera.scale = max(camera.scale, 0.01)

        # Apply velocity to camera
        camera.apply_velocity()

        # Calculate forces and apply acceleration
        for b in range(len(bodies)):
            for o in range(len(bodies)-1,b,-1):
                if merge and bodies[b].test_collision(bodies[o]):           # Merge setting check must precede collision check for optimization purposes (https://docs.python.org/3/library/stdtypes.html#boolean-operations-and-or-not)
                    bodies[b].merge(bodies[o])
                    bodies.pop(o)
                    if settings_window.alive:
                        settings_window.set_bodies(len(bodies))
                else:
                    force = bodies[b].force_of(bodies[o],G)
                    acc = bodies[o].mass * force * time_factor
                    acc2 = bodies[b].mass * force * time_factor
                    bodies[b].apply_acceleration(acc)
                    bodies[o].apply_acceleration(-acc2)

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
