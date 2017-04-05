import ctypes


G = 0.5

Density = 0.1

# define starting window width and height
user32 = ctypes.windll.user32
monitor_width = user32.GetSystemMetrics(0)
monitor_height = user32.GetSystemMetrics(1)
width, height = int(monitor_width * 0.7), int(monitor_height * 0.8)
