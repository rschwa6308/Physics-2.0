import ctypes

G = 0.5

Density = 0.1

width, height = info.current_w // 2, info.current_h // 2

# define starting window width and height
<<<<<<< HEAD
global width, height
width, height = 1000, 800
=======
user32 = ctypes.windll.user32
monitor_width = user32.GetSystemMetrics(0)
monitor_height = user32.GetSystemMetrics(1)
width, height = int(monitor_width * 0.6), int(monitor_height * 0.75)

>>>>>>> refs/remotes/origin/master
