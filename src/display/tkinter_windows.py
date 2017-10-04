import os, tkinter as tk
from tkinter import filedialog, messagebox, colorchooser

from .json_saving import Save, load_save
from ..core.bodies import generate_bodies
from ..core.presets import Gradient, System


class Menu:
    def __init__(self, bodies, camera, dims, *args):
        self.bodies, self.camera, self.dims, self.alive = bodies, camera, dims, True
        self.create_root()
        self.root.protocol("WM_DELETE_WINDOW", self.destroy)
        self.configure(*args)

    def createEntryRange(self, *entryDetails):
        name, AttrName, Root, Row, Def1, Def2 = entryDetails
        frame = tk.Frame(Root)
        self.__dict__[AttrName] = tk.StringVar(value=Def1)
        self.__dict__[AttrName + '2'] = tk.StringVar(value=Def2)
        tk.Entry(frame, textvariable=self.__dict__[AttrName], justify='center').grid(row=0, column=0)
        tk.Label(frame, text=' to ').grid(row=0, column=1)
        tk.Entry(frame, textvariable=self.__dict__[AttrName + '2'], justify='center').grid(row=0, column=2)
        tk.Label(Root, text=name).grid(row=Row)
        frame.grid(row=Row, column=1)

    def findEntries(self, AttrName):
        return (float(self.__dict__[AttrName].get()), float(self.__dict__[AttrName + '2'].get()))

    def createLabelSlider(self, *sliderDetails):
        name, AttrName, Root, Row, From, To, Length, Val, Res = sliderDetails
        tk.Label(Root, text=name).grid(row=Row)
        self.__dict__[AttrName] = tk.Scale(Root, from_=From, to=To, orient=tk.HORIZONTAL, length=Length, resolution=Res)
        self.__dict__[AttrName].set(Val)
        self.__dict__[AttrName].grid(row=Row, column=1)

    def createBoolean(self, *Details):
        name, AttrName, Root, Row, Column, PadY, Grid, Val = Details
        self.__dict__[AttrName] = tk.BooleanVar(value=Val)
        if Grid:
            tk.Checkbutton(Root, text=name, variable=self.__dict__[AttrName]).grid(row=Row, column=Column, pady=PadY,
                                                                                   sticky=tk.W)
        else:
            Root.add_checkbutton(label=name, variable=self.__dict__[AttrName])

    def createColor(self, *Details):
        name, AttrName, Root, Row = Details
        frame = tk.Frame(Root)
        tk.Label(frame, text=name).grid(row=0, column=0)
        tk.Button(frame, text="Select Color", command=lambda: self.color_choice(AttrName + "Val")).grid(row=0, column=1,
                                                                                                        padx=5, pady=5)
        self.__dict__[AttrName + "Val"] = tk.StringVar(value='')
        tk.Label(frame, textvariable=self.__dict__[AttrName + "Val"]).grid(row=0, column=2)
        frame.grid(row=Row, columnspan=2)

    def destroy(self):
        self.root.destroy()
        self.alive = False


class CreateSystem(Menu):
    def create_root(self):
        self.root = tk.Toplevel()
        self.choices = {"System": ("Unary", "Binary", "Cluster"), "Gradient": ("Density", "Diffusion")}

    def configure(self, parent):
        self.parent, d = parent, list(self.choices.keys())[0]
        default = tk.StringVar(value=d)
        tk.Label(self.root, text="Choose system type:").grid(row=0, column=0)
        self.opt = tk.OptionMenu(self.root, default, *self.choices, command=lambda x: self.choice2(x))
        self.opt.grid(row=0, column=1)
        self.opt.config(width=8)
        self.choice2(d)

    def color_choice(self, AttrName):
        color = colorchooser.askcolor()
        if color != (None, None):
            c = tuple(int(x) for x in color[0])
            if c:
                self.__dict__[AttrName].set(str(c))
                self.__dict__[AttrName + 'True'] = c

    def choice2(self, chosen):
        c = self.choices[chosen]
        default = tk.StringVar(value=c[0])
        self.opt2 = tk.OptionMenu(self.root, default, *c, command=lambda x: self.details(chosen, x))
        self.opt2.grid(row=1, column=1)
        self.opt2.config(width=8)
        self.details(chosen, self.choices[chosen][0])

    def details(self, chosen, chosen2):  # Chosen is broad category, chosen2 is subcategory
        for x in self.root.grid_slaves():
            if int(x.grid_info()["row"]) > 1:
                x.grid_forget()
                x.destroy()
        root = tk.LabelFrame(self.root)
        self.createLabelSlider("Body Count: ", 'num', root, 2, 0, 200, 200, 100, 1)
        self.createEntryRange("Mass Range: ", 'mass_r', root, 3, 10, 15)
        row = 4  # Use this to track the number of rows used in the window
        if chosen == "Gradient":
            self.createColor('Color 1', 'color1', root, row);
            self.createColor('Color 2', 'color2', root, row + 1)
            self.color1Val.set("(255, 0, 0)");
            self.color2Val.set("(0, 0, 255)");
            self.color1ValTrue, self.color2ValTrue = (255, 0, 0), (0, 0, 255)
            row += 2
            if chosen2 == "Density":
                self.createEntryRange("Densities: ", 'densities', root, row, 0.1, 0.15)
                row += 1
        else:
            self.createEntryRange("Distance: ", 'dist_r', root, row, 100, 300)
            self.createLabelSlider("Density: ", 'density', root, row + 1, .01, 1, 200, .1, .01)
            row += 2
            if chosen2 in ["Binary", "Unary"]:
                self.createLabelSlider("Star Density: ", 'star_density', root, row, .01, 1, 200, .4, .01)
                self.createLabelSlider("Star Mass: ", 'star_mass', root, row + 1, 0, 10000, 200, 500, 50)
                row += 2
                if chosen2 == "Binary":
                    self.createLabelSlider("Star Mass 2: ", 'star_mass2', root, row, 0, 10000, 200, 500, 50)
                    row += 1
                else:
                    self.createBoolean('Circular?', 'circular', root, row, 0, 0, 1, 1)
        tk.Button(root, text="Submit", command=lambda: self.submit(chosen, chosen2)).grid(row=row, columnspan=2,
                                                                                          pady=10)
        root.grid(row=2, columnspan=2)

    def submit(self, chosen, chosen2):
        new_bodies, dims, num, mass_r = [], self.dims, self.num.get(), self.findEntries('mass_r')
        if chosen == "Gradient":
            colors = (self.color1ValTrue, self.color2ValTrue)
            if chosen2 == "Density":
                densities = self.findEntries('densities')
                new_bodies = Gradient(dims, num, mass_r, colors).preset('Density', densities)
            else:
                new_bodies = Gradient(dims, num, mass_r, colors).preset('Diffusion')
        else:
            dist_r, density = self.findEntries('dist_r'), self.density.get()
            if chosen2 == "Cluster":
                new_bodies = System(dims, num, mass_r, dist_r, density).preset('Cluster')
            else:
                star_density, star_mass = self.star_density.get(), self.star_mass.get()
                if chosen2 == "Binary":
                    star_mass2 = self.star_mass2.get()
                    new_bodies = System(dims, num, mass_r, dist_r, density).preset('Binary', (star_mass, star_mass2),
                                                                                   star_density)
                else:
                    circular = self.circular.get()
                    new_bodies = System(dims, num, mass_r, dist_r, density).preset('Unary', star_mass, star_density,
                                                                                   circular)
        if not self.bodies or messagebox.askokcancel("Discard Changes", "Are you sure you want to discard changes?"):
            self.bodies[:] = new_bodies
            for window in self.parent.properties_windows:
                window.destroy()
            self.parent.properties_windows = []
            self.parent.name.set("Unnamed Simulation")
            self.parent.filename = ''


class Settings(Menu):
    def create_root(self):
        self.root = tk.Tk()

    def configure(self, constants):
        self.root.title("Simulation Settings")
        self.properties_windows, self.physics_frame, G, COR, self.bg_color = [], tk.LabelFrame(self.root), *constants, (
        255, 255, 255)

        # Top Bar Menu
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self.menu.add_command(label="New", command=self.new_file)
        self.menu.add_command(label="Open", command=self.open_file)
        self.menu.add_command(label="Save", command=self.save)
        self.menu.add_command(label="Save As", command=self.save_as)

        self.submenu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Options", menu=self.submenu)
        self.submenu.add_command(label="Set Background Color", command=self.set_bg_color)
        self.createBoolean('Walls', 'walls', self.submenu, 0, 0, 0, 0, 0)
        self.createBoolean('Mutual Gravitation', 'gravity_on', self.submenu, 0, 0, 0, 0, 1)
        self.createBoolean('Gravitational Field', 'g_field', self.submenu, 0, 0, 0, 0, 0)

        # File Frame Content
        self.filename = ""
        self.name = tk.StringVar(value="Unnamed Simulation")
        tk.Label(self.root, textvariable=self.name).grid(row=0, column=0, columnspan=5000)

        # Physics Frame Content
        self.createLabelSlider('Gravity: ', 'gravity_slider', self.physics_frame, 0, -1000, 1000, 200, G * 100, 1)
        self.createLabelSlider('Time Factor (%): ', 'time_slider', self.physics_frame, 1, 0, 500, 200, 0, 1)
        self.createLabelSlider('Elasticity (CoR): ', 'COR_slider', self.physics_frame, 2, 0, 2, 200, COR, .01)
        self.createBoolean('Collisions', 'collision', self.physics_frame, 3, 1, 5, 1, 1)

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

    def new_file(self):
        x = create_menu("CreateSystem", self.bodies, self.camera, self.dims, self)

    def open_file(self):
        filename = filedialog.askopenfilename()
        if filename and (
            not self.bodies or messagebox.askokcancel("Discard Changes", "Are you sure you want to discard changes?")):
            self.filename = filename
            self.name.set(os.path.split(filename)[-1])
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

        self.createLabelSlider('Mass: ', 'mass_slider', self.root, 1, 1, self.body.mass * 10, 100, self.body.mass, 1)
        self.createLabelSlider('Density: ', 'density_slider', self.root, 2, .01, self.body.density * 10, 100,
                               self.body.density, .01)
        self.createBoolean('Velocity', 'velocity', self.root, 3, 0, 0, 1, 1)
        self.createBoolean('Acceleration', 'acceleration', self.root, 4, 0, 0, 1, 1)

        self.canvas = tk.Canvas(self.root, width=104, height=104)
        self.update_canvas()

        tk.Button(self.root, text="Focus", command=self.focus).grid(row=5, columnspan=3)
        tk.Button(self.root, text="Delete", command=self.delete_body).grid(row=6, columnspan=3)
        # TODO: Add option for tracking specific bodies

        self.W = 220
        self.H = 250
        self.root.geometry('%dx%d+%d+%d' % (self.W, self.H, self.dims[0] / 3 - 10 - self.W,
                                            self.dims[1] * 2 / 3 - 290 + (self.H + 31) * queue_position))

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
        for attr, color in ['velocity', 'blue'], ['acceleration', 'red']:
            a = getattr(self.body, attr)
            if getattr(self, attr).get() and a != (
            0, 0):  # If arrow is enabled and vector is not of length zero, draw the arrow using a logistic formula
                self.canvas.create_line(
                    (52, 52, *((52, 52) + 40 * (1 - 2 ** -(a.length() * 1000000 ** (attr[0] != 'v'))) * a.normalize())),
                    fill=color, arrow="last")
        self.canvas.grid(row=3, column=1, rowspan=2, columnspan=4)

    def merge(self):
        self.mass_slider.set(self.body.mass)
        self.mass_slider.config(to=self.body.mass * 10)
        self.density_slider.set(self.body.density)
        self.density_slider.config(to=self.body.density * 10)

    def update(self):
        self.root.update()
        try:
            self.body.mass, self.body.density = self.mass_slider.get(), self.density_slider.get()
        except:
            pass
        self.body.update_radius()
        self.update_canvas()


def create_menu(menu_type, *args):
    return globals()[menu_type](*args)
