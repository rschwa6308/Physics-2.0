import ctypes


G = 0.5

Density = 0.1

# define starting window width and height
user32 = ctypes.windll.user32

width, height = int(user32.GetSystemMetrics(0) * 0.8), int(user32.GetSystemMetrics(1) * 0.8)
