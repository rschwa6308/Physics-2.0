import json

class Save:
    def __init__(self, settings_window):
        cam = settings_window.camera
        
        self.data = {}
        self.data["settings"] = {
            "G": settings_window.gravity_slider.get(),
            "time factor": settings_window.time_slider.get(),
            "coefficient of restitution": settings_window.COR_slider.get(),
            "collision": settings_window.collision.get(),
            "background color": settings_window.bg_color,
            "walls": settings_window.walls.get(),
            "gravity": settings_window.gravity_on.get(),
            "gravitational field": settings_window.g_field.get(),
            "camera": {
                "position": list(cam.position),
                "scale": cam.scale
            }
        }
        
        self.data["bodies"] = []
        for b in settings_window.bodies:
            self.data["bodies"].append({
                "mass": b.mass,
                "radius": b.radius,
                "position": list(b.position),
                "velocity": list(b.velocity),
                "density": b.density,
                "color": b.color,
                "name": b.name
            })

    def save_as(self, filename):
        with open(filename, "w") as outfile:
            json.dump(self.data, outfile)
