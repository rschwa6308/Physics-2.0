import Tkinter as tk

from Presets import *




class Settings:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Universe Settings")

        self.root.protocol("WM_DELETE_WINDOW", self.destroy)
        self.alive = True

        tk.Label(self.root, text="Slide to change G").pack()
        self.gravity_slider = tk.Scale(self.root, from_=0, to = 100, orient=tk.HORIZONTAL, length=200)
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




def display(screen, bodies, (cam_position, cam_scale)):
    #clear last frame
    screen.fill(bg_color)

    #display all bodies
    for b in bodies:
        #screen.blit(b.image, b.position)
        # b.draw_on(screen)
        # calculate coordinates and radius adjusted for camera
        x = (int(b.position[0]) - cam_position[0])
        x = int((x - width / 2) * cam_scale + width / 2)
        y = int(b.position[1]) - cam_position[1]
        y = int((y - height / 2) * cam_scale + height / 2)
        radius = int(b.radius * cam_scale)
        pg.draw.circle(screen, b.color, [x, y], radius, 0)

    #flip display
    pg.display.update()



def main():

    # initialize tkinter window
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
    #                   (star_mass, star_density, planets, min_mass, max_mass, min_distance, max_distance)
    bodies = star_system(100, 0.001, 10, 1, 10, 100, 400)


    # initialize screen
    screen = pg.display.set_mode((width, height))
    pg.display.set_caption("Physics Simulator")
    icon = pg.image.load("Assets/physics.png")
    pg.display.set_icon(icon)


    # initialize game clock and set tick to 60
    clock = pg.time.Clock()
    fps = 60

    done = False
    while not done:
        clock.tick(fps)

        if settings_window.alive:           # update tk window if alive
            settings_window.update()
            G = settings_window.get_gravity()
            fps = settings_window.get_time()

        # user input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    cam_velocity[0] = -3 / cam_scale
                elif event.key == pg.K_RIGHT:
                    cam_velocity[0] = 3  / cam_scale
                elif event.key == pg.K_UP:
                    cam_velocity[1] = -3 / cam_scale
                elif event.key == pg.K_DOWN:
                    cam_velocity[1] = 3 / cam_scale
            elif event.type == pg.KEYUP:
                if event.key == pg.K_LEFT:
                    cam_velocity[0] = 0
                elif event.key == pg.K_RIGHT:
                    cam_velocity[0] = 0
                elif event.key == pg.K_UP:
                    cam_velocity[1] = 0
                elif event.key == pg.K_DOWN:
                    cam_velocity[1] = 0
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

        # calculate forces and apply acceleration
        for body in bodies:
            for other in bodies:
                if other is not body:
                    if body.test_collision(other):
                        body.merge(other)
                        bodies.remove(other)
                    else:
                        acceleration = body.effect_of(other, G)
                        body.apply_acceleration(acceleration)

        # apply velocity (update position)
        for body in bodies:
            body.apply_velocity()


    pg.quit()
    if settings_window.alive: settings_window.destroy()         # destroy tk window if alive








if __name__ == "__main__":
    main()
