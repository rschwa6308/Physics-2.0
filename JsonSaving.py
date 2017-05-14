import json

class Save:
    def __init__(self, settings_window):
        grav = settings_window.get_gravity()
        time = settings_window.get_time()
        cam = settings_window.camera
        bods = settings_window.bodies
        
        self.data = {}
        self.data["settings"] = {
            "G": grav,
            "time factor": time,
            "camera": {
                "position": [cam.position[n] for n in (0, 1)],
                "scale": cam.scale
            }
        }
        
        self.data["bodies"] = []
        for b in bods:
            self.data["bodies"].append(
                {
                    "mass": b.mass,
                    "radius": b.radius,
                    "position": [b.position[n] for n in (0, 1)],
                    "velocity": [b.velocity[n] for n in (0, 1)],
                    "density": b.density,
                    "color": b.color,
                    "name": b.name
                }
            )

    def save_as(self, filename):
        with open(filename, "w") as outfile:
            json.dump(self.data, outfile)