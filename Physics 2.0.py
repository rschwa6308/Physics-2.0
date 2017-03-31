from Presets import *


def display(screen, bodies):
    # Clear last frame
    screen.fill(bg_color)

    # Display all bodies
    for b in bodies:
        #screen.blit(b.image, b.position)
        b.draw_on(screen)

    # Update display
    pg.display.update()



def main():

    # Construct bodies list
    # bodies = [
    #     Body(10, 10, [200, 200], [0, 0]),
    #     Body(10, 20, [60, 60], [0, 0]),
    #     Body(10, 50, [100, 150], [0, 0])
    # ]
    # (star_mass, star_density, planets, min_mass, max_mass, min_distance, max_distance)
    bodies = star_system(1000, 0.04, 100, 1, 10, 100, 400)


    # initialize screen
    screen = pg.display.set_mode((width, height))

    # initialize game clock and set tick to 60
    clock = pg.time.Clock()
    clock.tick(60)

    done = False
    while not done:
        clock.tick(60)
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
                        acceleration = body.effect_of(other)
                        body.apply_acceleration(acceleration)

        # apply velocity (update position)
        for body in bodies:
            body.apply_velocity()


    pg.quit()








if __name__ == "__main__":
    main()
