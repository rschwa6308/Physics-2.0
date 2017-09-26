import os, tkinter as tk
from tkinter import filedialog, messagebox, colorchooser

from .json_saving import Save, load_save
from ..core.bodies import generate_bodies

class Menu:
    def __init__(self, bodies, camera, dims, *args):
        self.bodies, self.camera, self.dims, self.alive = bodies, camera, dims, True
        self.create_root()
        self.root.protocol("WM_DELETE_WINDOW", self.destroy)
        self.configure(*args)

    def createLabelSlider(self, sliderDetails):
        name, AttrName, Root, Row, From, To, Length, Val, Res = sliderDetails
        tk.Label(Root, text=name).grid(row=Row)
        self.__dict__[AttrName] = tk.Scale(Root, from_=From, to=To, orient=tk.HORIZONTAL, length=Length, resolution=Res)
        self.__dict__[AttrName].set(Val)
        self.__dict__[AttrName].grid(row=Row, column=1)

    def createBoolean(self, Details):
        name, AttrName, Root, Row, Column, PadY, Grid, Val = Details
        self.__dict__[AttrName] = tk.BooleanVar()
        self.__dict__[AttrName].set(Val)
        if Grid: tk.Checkbutton(Root, text=name, variable=self.__dict__[AttrName]).grid(row=Row, column=Column, pady=PadY, sticky=tk.W)
        else: Root.add_checkbutton(label=name, variable=self.__dict__[AttrName])

    def destroy(self):
        self.root.destroy()
        self.alive = False
        

class Settings(Menu):
    def create_root(self):
        self.root = tk.Tk()
    
    def configure(self, constants):
        self.root.title("Simulation Settings")
        self.properties_windows, self.physics_frame, G, COR, self.bg_color = [], tk.LabelFrame(self.root), *constants,  (255,255,255)

        # Top Bar Menu
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self.menu.add_command(label="Open", command=self.open_file)
        self.menu.add_command(label="Save", command=self.save)
        self.menu.add_command(label="Save As", command=self.save_as)

        self.submenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Options", menu=self.submenu)
        self.submenu.add_command(label="Set Background Color", command=self.set_bg_color)
        self.createBoolean(('Walls', 'walls', self.submenu, 0,0,0,0,0))
        self.createBoolean(('Mutual Gravitation', 'gravity_on', self.submenu, 0,0,0,0,1))
        self.createBoolean(('Gravitational Field', 'g_field', self.submenu, 0,0,0,0,0))

        # File Frame Content
        self.filename = ""
        self.name = tk.StringVar()
        self.name.set("Unnamed Simulation")
        tk.Label(self.root, textvariable=self.name).grid(row=0, column=0, columnspan=5000)

        # Physics Frame Content
        self.createLabelSlider(('Gravity: ', 'gravity_slider', self.physics_frame, 0, -1000, 1000, 200, G*100, 1))
        self.createLabelSlider(('Time Factor (%): ', 'time_slider', self.physics_frame, 1, 0, 500, 200, 0, 1))
        self.createLabelSlider(('Elasticity (CoR): ', 'COR_slider', self.physics_frame, 2, 0, 2, 200, COR, .01))
        self.createBoolean(('Collisions', 'collision', self.physics_frame, 3,1,5,1,1))

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
            '%dx%d+%d+%d' % (305, 260, self.dims[0] / 3 - 315, self.dims[1] / 6 - 20))

    def set_body_count(self):
        self.bodies_label_text.set("Bodies: " + str(len(self.bodies)))

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
                self.bodies[:] = generate_bodies(load_save(self, file))

    def set_bg_color(self):
        new = colorchooser.askcolor()[0]
        if new:
            self.bg_color = new

    def quit(self):
        pg.quit()
        self.destroy()

    def update(self):
        self.set_body_count()
        self.root.update()


class BodyProperties(Menu):
    def create_root(self):
        self.root = tk.Toplevel()
        
    def configure(self, queue_position, body):
        self.body = body
        self.root.title(self.body.name.title() if self.body.name else "Unnamed Body")

        self.createLabelSlider(('Mass: ', 'mass_slider', self.root, 1, 1, self.body.mass*10, 100, self.body.mass, 1))
        self.createLabelSlider(('Density: ', 'density_slider', self.root, 2, .01, self.body.density * 10, 100, self.body.density, .01))
        self.createBoolean(('Velocity', 'velocity', self.root, 3,0,0,1,1))
        self.createBoolean(('Acceleration', 'acceleration', self.root, 4,0,0,1,1))

        self.canvas = tk.Canvas(self.root, width=104, height=104)
        self.update_canvas()

        tk.Button(self.root, text="Focus", command=self.focus).grid(row=5, columnspan=3)
        tk.Button(self.root, text="Delete", command=self.delete_body).grid(row=6, columnspan=3)
        # TODO: Add option for tracking specific bodies

        self.W = 220
        self.H = 250
        self.root.geometry('%dx%d+%d+%d' % (self.W, self.H, self.dims[0] / 3 - 10 - self.W,
                                            self.dims[1] * 2/3 - 290 + (self.H + 31) * queue_position))

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
        for attr, color in ['velocity','blue'],['acceleration','red']:
            a = getattr(self.body, attr)
            if getattr(self, attr).get() and a != (0,0): # If arrow is enabled and vector is not of length zero, draw the arrow using a logistic formula
                self.canvas.create_line((52, 52, *((52,52)+40*(1-2**-(a.length()*1000000**(attr[0]!='v')))*a.normalize())), fill=color, arrow="last")
        self.canvas.grid(row=3, column=1, rowspan=2, columnspan=4)

    def update(self):
        self.root.update()
        try: self.body.mass, self.body.density = self.mass_slider.get(), self.density_slider.get()
        except: pass
        self.body.update_radius()
        self.update_canvas()

def create_menu(menu_type, *args):
    return globals()[menu_type](*args)
