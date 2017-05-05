import json


test_save = {}
test_save["settings"] = {
    "G": 100,
    "time factor": 1,
    "camera": {
        "position": (0, 0),
        "scale factor": 1
    }
}

test_save["bodies"] = [
    ]



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
                "position": cam.position,
                "scale": cam.scale
            }
        }
        
        self.data["bodies"] = []
        for b in bods:
            self.data["bodies"].append(
                {
                    "mass": b.mass,
                    "radius": b.radius,
                    "position": b.position,
                    "velocity": b.velocity,
                    "density": b.density,
                    "color": b.color,
                    "name": b.name
                }
            )



if __name__ == "__main__":
    with open("test save.sim", "w") as outfile:
        json.dump(data, outfile)


