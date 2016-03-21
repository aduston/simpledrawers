from OCC import gp, TopLoc
from OCC.Display.SimpleGui import init_display
from OCC.TopoDS import TopoDS_Builder, TopoDS_Compound
from drawer import make_drawer
from drawer_box import make_drawer_box, BACK_INSET
from constants import THICKNESS_0, THICKNESS_1

def _move(shape, x, y, z):
    tr = gp.gp_Trsf()
    tr.SetTranslation(gp.gp_Vec(x, y, z))
    loc = TopLoc.TopLoc_Location(tr)
    shape.Move(loc)

def make_drawers(dx, dy, dz, arrangement):
    air_space = 0.05
    available_z_space = dz - THICKNESS_0 * (len(arrangement) + 1)
    drawer_space_height = available_z_space / len(arrangement)
    drawer_depth = dy - BACK_INSET - THICKNESS_1
    offsets = []
    for i in range(len(arrangement) - 1):
        offsets.append(THICKNESS_0 + (i + 1) * (drawer_space_height + THICKNESS_0))
    drawer_box = make_drawer_box(dx, dy, dz, offsets)
    drawers = []
    for level, num_drawers in enumerate(arrangement):
        drawer_width = (dx - THICKNESS_0 * 2 - (num_drawers + 1) * air_space) / float(num_drawers)
        z_pos = dz - (level + 1) * (THICKNESS_0 + drawer_space_height) + air_space
        for drawer_index in range(num_drawers):
            drawer = make_drawer(
                drawer_width,
                drawer_depth,
                drawer_space_height - 2 * air_space)
            _move(drawer,
                  THICKNESS_0 + air_space + (air_space + drawer_width) * drawer_index,
                  0, z_pos)
            drawers.append(drawer)

    builder = TopoDS_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    builder.Add(compound, drawer_box)
    for drawer in drawers:
        builder.Add(compound, drawer)
    return compound

paper_size = (11 * 2.54, 8.5 * 2.54)
drawers = make_drawers(
    paper_size[0] + 2 + THICKNESS_0 * 2,
    paper_size[1] + 2 + THICKNESS_0 * 2 + THICKNESS_1 + BACK_INSET,
    24,
    [3, 1, 1])

display, start_display, add_menu, add_function_to_menu = init_display()
display.DisplayShape(drawers, update=True)
start_display()

