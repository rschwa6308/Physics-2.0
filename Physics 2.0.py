import tkinter as tk

from Presets import *
from Constants import *

class Settings:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Universe Settings")

        self.root.protocol("WM_DELETE_WINDOW", self.destroy)
        self.alive = True

        tk.Label(self.root, text="Slide to change G").pack()
        self.gravity_slider = tk.Scale(self.root, from_=0, to = 1000, orient=tk.HORIZONTAL, length=200)
        self.gravity_slider.set(G*100)
        self.gravity_slider.pack()

        tk.Label(self.root, text="Slide to change clock speed").pack()
        self.time_slider = tk.Scale(self.root, from_=1, to=300, orient=tk.HORIZONTAL, length=200)
        self.time_slider.set(60)
        self.time_slider.pack()

    def get_gravity(self):
        try:
            return self.gravity_slider.get() / 100.0
        except:
            return G

    def get_time(self):
        try:
            return self.time_slider.get()
        except:
            return 60

    def update(self):
        self.root.update()

    def destroy(self):
        self.alive = False
        self.root.destroy()

def display(screen, bodies, camera):
    #clear last frame
    screen.fill(bg_color)           # comment out this line for a fun time ;)

    # Display all bodies
    cam_position, cam_scale = camera
    for b in bodies:
        #screen.blit(b.image, b.position)
        # b.draw_on(screen)
        # calculate coordinates and radius adjusted for camera
        x = b.position[0] - cam_position[0]
        x = (x - width / 2) * cam_scale + width / 2
        y = b.position[1] - cam_position[1]
        y = (y - height / 2) * cam_scale + height / 2
        radius = b.radius * cam_scale
        pg.draw.circle(screen, b.color, (int(x), int(y)), int(radius), 0)
        
    # Update display
    pg.display.update()



def main():
    global width, height
    
    # Initialize tkinter window
    settings_window = Settings()

    # initialize camera variables
    cam_position = [0, 0]
    cam_velocity = [0, 0]
    cam_scale = 1

    # construct bodies list

    # bodies = [
    #     Body(1000, [1000, 500], [0, 0]),
    #     Body(1000, [60, 800], [0, 0]),
    #     Body(1000, [500, 150], [0, 0])
    # ]
    # (star_mass, star_density, planets, min_mass, max_mass, min_distance, max_distance)
    bodies = star_system(1000, 0.04, 150, 1, 10, 100, 500, planet_density=0.1)
    
    # Initialize screen
    icon = pg.image.load('AtomIcon.png')
    pg.display.set_icon(icon)
    screen = pg.display.set_mode((width, height), pg.RESIZABLE)
    pg.display.set_caption("Physics Simulator 2")

    clock = pg.time.Clock()
    fps = 60

    scroll = V2(0,0)
    scroll_right, scroll_left, scroll_down, scroll_up = 0,0,0,0
    scroll_constant = 2.5
    done = False
    while not done:
        clock.tick(fps)

        if settings_window.alive:
            settings_window.update()
            G = settings_window.get_gravity()
            fps = settings_window.get_time()

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
                    cam_velocity[0] = -3 / cam_scale
                elif event.key == pg.K_RIGHT:
                    cam_velocity[0] = 3  / cam_scale
                elif event.key == pg.K_UP:
                    cam_velocity[1] = -3 / cam_scale
                elif event.key == pg.K_DOWN:
                    cam_velocity[1] = 3 / cam_scale
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
                    cam_velocity[0] = 0
                elif event.key == pg.K_RIGHT:
                    cam_velocity[0] = 0
                elif event.key == pg.K_UP:
                    cam_velocity[1] = 0
                elif event.key == pg.K_DOWN:
                    cam_velocity[1] = 0
            elif event.type == pg.QUIT:
                done = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 4:
                    cam_scale *= 1.1
                    cam_scale = min(cam_scale, 100)
                elif event.button == 5:
                    cam_scale /= 1.1
                    cam_scale = max(cam_scale, 0.01)


        # apply velocity to camera
        cam_position[0] += cam_velocity[0]
        cam_position[1] += cam_velocity[1]

        # display current frame
        display(screen, bodies, (cam_position, cam_scale))

        # Calculate forces and apply acceleration
        for b in range(len(bodies)):
            for o in range(len(bodies)-1,b,-1):
                if bodies[b].test_collision(bodies[o]):
                    bodies[b].merge(bodies[o])
                    bodies.pop(o)
                else:
                    force = bodies[b].force_of(bodies[o],G)
                    acc = bodies[o].mass * force
                    acc2 = bodies[b].mass * force
                    bodies[b].apply_acceleration(acc)
                    bodies[o].apply_acceleration(-acc2)
        
        # Apply velocity (update position)
        for body in bodies:
            body.apply_velocity()
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
