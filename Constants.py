from pygame import init as pygameInit
from pygame.display import Info as WindowDims
G = 0.5

Density = 0.1

# Set window to half of monitor dimensions
pygameInit()
info = WindowDims()
width, height = info.current_w // 2, info.current_h // 2
