import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import colorchooser
import os

from Constants import *
from JsonSaving import *
from Bodies import *

class Settings:
    def __init__(self, bodies, camera):
        self.bodies = bodies
        self.camera = camera

        self.root = tk.Tk()
        self.root.title("Simulation Settings")

        self.root.protocol("WM_DELETE_WINDOW", self.destroy)
        self.alive = True

        self.physics_frame = tk.LabelFrame(self.root)

        self.bg_color = bg_color
        self.walls = tk.BooleanVar(False)
        self.gravity_on = tk.BooleanVar()
        self.gravity_on.set(True)
        self.g_field = tk.BooleanVar(False)

        # Top Bar Menu
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self.menu.add_command(label="Open", command=self.open_file)
        self.menu.add_command(label="Save", command=self.save)
        self.menu.add_command(label="Save As", command=self.save_as)

        self.submenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Options", menu=self.submenu)
        self.submenu.add_command(label="Set Background Color", command=self.set_bg_color)
        self.submenu.add_checkbutton(label="Walls", variable=self.walls)
        self.submenu.add_checkbutton(label="Mutual Gravitation", variable=self.gravity_on)
        self.submenu.add_checkbutton(label="Gravitational Field", variable=self.g_field)

        # File Frame Content
        self.filename = ""
        self.name = tk.StringVar()
        self.name.set("Unnamed Simulation")
        tk.Label(self.root, textvariable=self.name).grid(row=0, column=0, columnspan=5000)

        # Physics Frame Content
        tk.Label(self.physics_frame, text="Gravity: ").grid(row=0, column=0)
        self.gravity_slider = tk.Scale(self.physics_frame, from_=-1000, to=1000, orient=tk.HORIZONTAL, length=200)
        self.gravity_slider.set(G * 100)
        self.gravity_slider.grid(row=0, column=1)

        tk.Label(self.physics_frame, text="Time Factor (%): ").grid(row=1, sticky=tk.E)
        self.time_slider = tk.Scale(self.physics_frame, from_=-0, to=500, orient=tk.HORIZONTAL,
                                    length=200)  # from_ can be set negative for rewind
        self.time_slider.set(0)
        self.time_slider.grid(row=1, column=1)

        tk.Label(self.physics_frame, text="Elasticity (CoR): ").grid(row=2, column=0)
        self.COR_slider = tk.Scale(self.physics_frame, from_=0, to=2, resolution=0.01, orient=tk.HORIZONTAL, length=200)
        self.COR_slider.set(COR)
        self.COR_slider.grid(row=2, column=1)

        self.collision = tk.IntVar()
        self.collision.set(1)
        self.collision_checkbutton = tk.Checkbutton(self.physics_frame, text="Collisions", variable=self.collision)
        self.collision_checkbutton.grid(row=3, column=1, pady=5, sticky=tk.W)

        self.bodies_label_text = tk.StringVar()
        self.bodies_label = tk.Label(self.physics_frame, textvariable=self.bodies_label_text)
        self.bodies_label.grid(row=3, column=0, pady=5)

        # Grid Frames
        self.physics_frame.grid(row=1, sticky=tk.W)

        # Misc Buttons
        tk.Button(self.root, text="Move Cam to COM", command=self.center_cam).grid(row=2, column=0)

        tk.Button(self.root, text="Quit", command=self.quit).grid(row=3, column=0, rowspan=1, columnspan=1, pady=20)

        # Set window size and screen position
        self.root.geometry(
            '%dx%d+%d+%d' % (305, 260, monitor_width / 2 - width / 2 - 315, monitor_height / 2 - height / 2 - 20))

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

    def get_COR(self):
        try:
            return self.COR_slider.get()
        except:
            return COR

    def get_collision(self):
        return self.collision.get()

    def set_bodies(self, n):
        self.bodies_label_text.set("Bodies: " + str(n))

    def center_cam(self):
        self.camera.move_to_com(self.bodies)

    def save(self):
        if self.filename == "":
            self.save_as()
        else:
            save_object = Save(self)
            save_object.save_as(self.filename)

    def save_as(self):
        save_object = Save(self)
        filename = filedialog.asksaveasfilename(defaultextension=".sim",
                                                filetypes=(("Simulation file", "*.sim"), ("All files", "*.*")))
        if filename:
            self.filename = filename
            self.name.set(os.path.split(filename)[-1])
            save_object.save_as(filename)

    def open_file(self):
        filename = filedialog.askopenfilename()
        self.filename = filename
        self.name.set(os.path.split(filename)[-1])
        if filename:
            for window in self.properties_windows:
                window.destroy()
            self.properties_windows = []
            with open(filename) as file:
                data = json.load(file)
                self.gravity_slider.set(data["settings"]["G"] * 100.0)
                self.time_slider.set(data["settings"]["time factor"] * 100.0)
                cam_data = data["settings"]["camera"]
                self.camera.position = cam_data["position"]
                self.camera.scale = cam_data["scale"]
                self.bg_color = data["settings"]["background color"] if "background color" in data["settings"] else (255,255,255)
                self.bodies[:] = [Body(b["mass"], b["position"], b["velocity"], b["density"], b["color"], b["name"]) for b
                                  in data["bodies"]]

    def set_bg_color(self):
        new = colorchooser.askcolor()[0]
        if new:
            self.bg_color = new

    def quit(self):
        pg.quit()
        self.destroy()

    def update(self):
        self.set_bodies(len(self.bodies))
        self.root.update()

    def destroy(self):
        self.alive = False
        self.root.destroy()


class BodyProperties:
    def __init__(self, body, bodies, queue_position, camera):
        self.camera = camera
        self.body = body
        self.bodies = bodies

        self.root = tk.Toplevel()
        self.root.title(self.body.name.title() if self.body.name is not None else "Unnamed Body")

        self.root.protocol("WM_DELETE_WINDOW", self.destroy)
        self.alive = True

        tk.Label(self.root, text="Mass: ").grid(row=1)
        self.mass_slider = tk.Scale(self.root, from_=1, to=self.body.mass * 10, orient=tk.HORIZONTAL, length=100)
        self.mass_slider.set(self.body.mass)
        self.mass_slider.grid(row=1, column=1)

        tk.Label(self.root, text="Density: ").grid(row=2)
        self.density_slider = tk.Scale(self.root, from_=.01, to=self.body.density * 10, resolution=0.01, orient=tk.HORIZONTAL, length=100)
        self.density_slider.set(self.body.density)
        self.density_slider.grid(row=2, column=1)

        self.velocity = tk.BooleanVar()
        self.velocity.set(True)
        self.velocity_checkbutton = tk.Checkbutton(self.root, text="Velocity", variable=self.velocity)
        self.velocity_checkbutton.grid(row=3, column=0, sticky=tk.W)

        self.acceleration = tk.BooleanVar()
        self.acceleration.set(True)
        self.acceleration_checkbutton = tk.Checkbutton(self.root, text="Acceleration", variable=self.acceleration)
        self.acceleration_checkbutton.grid(row=4, column=0, sticky=tk.W)

        self.canvas = tk.Canvas(self.root, width=104, height=104)
        self.update_canvas()

        tk.Button(self.root, text="Focus", command=self.focus).grid(row=5, columnspan=3)
        tk.Button(self.root, text="Delete", command=self.delete_body).grid(row=6, columnspan=3)

        self.width = 220
        self.height = 250
        self.root.geometry('%dx%d+%d+%d' % (self.width, self.height, monitor_width / 2 - width / 2 - 10 - self.width,
                                            monitor_height / 2 - 290 + (self.height + 31) * queue_position))

    def focus(self):
        self.camera.move_to_body(self.body)

    def delete_body(self):
        if messagebox.askokcancel("Delete Body", 'Are you sure you want to delete "{}"?'.format(self.body.name)):
            self.bodies.remove(self.body)
            self.destroy()

    def update_canvas(self):
        self.canvas.delete("all")
        self.canvas.create_oval((2, 2, 102, 102))
        for c in ((52, 2, 52, 102), (2, 52, 102, 52)):
            self.canvas.create_line(c, fill="Dark Gray", dash=(2, 2))
        for attr in ['velocity','acceleration']:
            if getattr(self, attr).get():
                mag = getattr(self.body, attr).length()
                scale_factor = 40 * (1 - 2 ** -(mag * (1 if attr=='velocity' else 1000000) ))/ mag if mag else 0
                x, y = scale_factor * getattr(self.body, attr)
                self.canvas.create_line((52, 52, 52 + x, 52 + y), fill="Blue" if attr=='velocity' else "Red", arrow="last")
        self.canvas.grid(row=3, column=1, rowspan=2, columnspan=4)

    def update(self):
        self.root.update()
        self.body.mass = self.mass_slider.get()
        self.body.density = self.density_slider.get()
        self.body.update_radius()
        self.update_canvas()

    def destroy(self):
        self.root.destroy()
        self.alive = False
