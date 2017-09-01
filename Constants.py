import ctypes

G = 0.5

Density = 0.1

COR = 1.0         # Coefficient of Restitution (https://en.wikipedia.org/wiki/Coefficient_of_restitution)

# define starting window width and height
try:
    # Windows
    import ctypes
    dim = ctypes.windll.user32.GetSystemMetrics
    monitor_width, monitor_height = dim(0), dim(1)
except:
    # Linux
    import subprocess, re
    output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0]
    monitor_width, monitor_height = re.findall(r'[0-9]+',str(output))

width, height = int(monitor_width * 0.6), int(monitor_height * 0.75)

# Set simulation hard clock speed (fps)
clock_speed = 144
