import ctypes

G = 0.5

Density = 0.1

# define starting window width and height
<<<<<<< HEAD
<<<<<<< HEAD
=======
global width, height
width, height = 1000, 800
>>>>>>> refs/remotes/rschwa6308/Single-Threading-Time-Control
user32 = ctypes.windll.user32
monitor_width = user32.GetSystemMetrics(0)
monitor_height = user32.GetSystemMetrics(1)
width, height = int(monitor_width * 0.6), int(monitor_height * 0.75)

<<<<<<< HEAD
=======
global width, height
width, height = 1000, 800
>>>>>>> refs/remotes/rschwa6308/Single-Threading-Time-Control
=======
# Set simulation hard clock speed (fps)
clock_speed = 144
>>>>>>> refs/remotes/rschwa6308/Single-Threading-Time-Control
