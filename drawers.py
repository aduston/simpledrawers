from OCC.Display.SimpleGui import init_display
from drawer import make_drawer

display, start_display, add_menu, add_function_to_menu = init_display()
drawer = make_drawer(20, 30, 10)

display.DisplayShape(drawer, update=True)
start_display()

