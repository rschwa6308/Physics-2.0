from Presets import *
from Constants import *


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

    global width, height

    # Construct bodies list
    # bodies = [
    #     Body(10, 10, [200, 200], [0, 0]),
    #     Body(10, 20, [60, 60], [0, 0]),
    #     Body(10, 50, [100, 150], [0, 0])
    # ]
    # (star_mass, star_density, planets, min_mass, max_mass, min_distance, max_distance)
    bodies = star_system(1000, 0.04, 100, 1, 10, 100, 400)

    
    # Initialize screen
    icon = pg.image.load('AtomIcon.png')
    pg.display.set_icon(icon)
    screen = pg.display.set_mode((width, height), pg.RESIZABLE)
    pg.display.set_caption("Physics Simulator 2.0")
    

    # Initialize game clock and set tick to 60
    clock = pg.time.Clock()
    clock.tick(60)

    scroll = [0,0]
    scroll_right, scroll_left, scroll_down, scroll_up = 0,0,0,0
    scroll_constant = 2.5
    done = False
    while not done:
        clock.tick(60)
        # user input
        for event in pg.event.get():
            if event.type == pg.VIDEORESIZE:
                
                width, height = event.w, event.h
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_d:
                    scroll_right = 1 
                elif event.key == pg.K_a:
                    scroll_left = 1
                elif event.key == pg.K_w:
                    scroll_up = 1
                elif event.key == pg.K_s:
                    scroll_down = 1
            elif event.type == pg.KEYUP:
                if event.key == pg.K_d:
                    scroll_right = 0
                elif event.key == pg.K_a:
                    scroll_left = 0
                elif event.key == pg.K_w:
                    scroll_up = 0
                elif event.key == pg.K_s:
                    scroll_down = 0
            elif event.type == pg.QUIT:
                done = True

        # Display current frame
        display(screen, bodies)

        # Calculate forces and apply acceleration
        for body in bodies:
            for other in bodies:
                if other is not body:
                    if body.test_collision(other):
                        body.merge(other)
                        bodies.remove(other)
                    else:
                        acceleration = body.effect_of(other)
                        body.apply_acceleration(acceleration)

        # Apply velocity (update position)
        for body in bodies:
            body.apply_velocity()
            body.position[0] += scroll[0]
            body.position[1] += scroll[1]


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



if __name__ == "__main__":
    main()
