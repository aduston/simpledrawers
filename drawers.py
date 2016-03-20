from OCC.Display.SimpleGui import init_display
from drawer import make_drawer
from drawer_box import make_drawer_box

display, start_display, add_menu, add_function_to_menu = init_display()
# drawer = make_drawer(20, 30, 10)
drawer_box = make_drawer_box(30, 25, 40, [10, 20])

display.DisplayShape(drawer_box, update=True)
start_display()

