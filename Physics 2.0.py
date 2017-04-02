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


    def update(self):
        self.root.update()

    def destroy(self):
        self.alive = False
        self.root.destroy()




def display(screen, bodies):
    #clear last frame
    screen.fill(bg_color)

    #display all bodies
    for b in bodies:
        #screen.blit(b.image, b.position)
        b.draw_on(screen)

    #flip display
    pg.display.update()



def main():

    # initialize tkinter window
    settings_window = Settings()


    # construct bodies list
    # bodies = [
    #     Body(10, 10, [200, 200], [0, 0]),
    #     Body(10, 20, [60, 60], [0, 0]),
    #     Body(10, 50, [100, 150], [0, 0])
    # ]
    #                   (star_mass, star_density, planets, min_mass, max_mass, min_distance, max_distance)
    bodies = star_system(1000, 0.01, 100, 1, 10, 100, 400)


    # initialize screen
    screen = pg.display.set_mode((width, height))
    pg.display.set_caption("Physics Simulator")
    icon = pg.image.load("Assets/physics.png")
    pg.display.set_icon(icon)


    # initialize game clock and set tick to 60
    clock = pg.time.Clock()

    done = False
    while not done:
        clock.tick(60)

        if settings_window.alive:           # update tk window if alive
            settings_window.update()
            try:
                G = settings_window.gravity_slider.get() / 100.0
            except:
                pass

        # user input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True

        # display current frame
        display(screen, bodies)

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