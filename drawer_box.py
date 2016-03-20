import math
from OCC import gp, TopLoc
from OCC.gp import gp_Pnt
from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.TopoDS import TopoDS_Builder, TopoDS_Compound
from constants import THICKNESS_0, THICKNESS_1

FINGER_WIDTH = 0.8
BACK_SPACE = 1.0
SEPARATOR_NOTCH_DEPTH = 0.2
BACK_NOTCH_DEPTH = THICKNESS_0 / 2.0
BACK_INSET = 0.3
SAW_RADIUS = 8.

_box = lambda *args: BRepPrimAPI_MakeBox(*args).Shape()
_cut = lambda *args: BRepAlgoAPI_Cut(*args).Shape()
_pnt = gp_Pnt

def make_drawer_box(dx, dy, dz, separator_offsets):
    """Makes a box to contain simple drawers.

    Args:
        dx (float): The total outer width of the drawer box
        dy (float): The total outer depth of the drawer box
        dz (float): The total outer height of the drawer box
        separator_offsets (List[float]): The distance from 
            the outer bottom of the drawer box to the top of
            each drawer separator.

    Returns:
        A TopoDS_Compound representing the drawer box.
    """
    pieces = [
        _make_side(dx, dy, dz, separator_offsets, True),
        _make_side(dx, dy, dz, separator_offsets, False),
        _make_topbottom(dx, dy, dz, True),
        _make_topbottom(dx, dy, dz, False),
        _make_back(dx, dy, dz)
    ]
    for separator_offset in separator_offsets:
        pieces.append(_make_separator(dx, dy, separator_offset))

    builder = TopoDS_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    for piece in pieces:
        builder.Add(compound, piece)
    return compound

def _make_side(dx, dy, dz, separator_offsets, is_left):
    side = _box(THICKNESS_0, dy, dz)
    side = _cut_side_fingers(side, 0, dy)
    side = _cut_side_fingers(side, dz - THICKNESS_0, dy)
    for separator_offset in separator_offsets:
        side = _cut_separator_notch(side, dy, separator_offset, is_left)
    side = _cut_side_back_notch(side, dy, dz, is_left)
    if not is_left:
        _move(side, dx - THICKNESS_0, 0, 0)
    return side

def _cut_side_fingers(side, z, dy):
    side = _cut(side, _box(_pnt(0, dy - BACK_SPACE, z), THICKNESS_0, BACK_SPACE, THICKNESS_0))
    offset = dy - BACK_SPACE - FINGER_WIDTH * 2
    while offset > -FINGER_WIDTH:
        side = _cut(side, _box(_pnt(0, offset, z), THICKNESS_0, FINGER_WIDTH, THICKNESS_0))
        offset -= FINGER_WIDTH * 2
    return side

def _cut_separator_notch(side, dy, separator_offset, is_left):
    x = THICKNESS_0 - SEPARATOR_NOTCH_DEPTH if is_left else 0
    saw_dy = math.sqrt(2 * SAW_RADIUS * SEPARATOR_NOTCH_DEPTH -
                       math.pow(SEPARATOR_NOTCH_DEPTH, 2))
    side = _cut(side, _box(_pnt(x, 0, separator_offset - THICKNESS_0),
                           SEPARATOR_NOTCH_DEPTH,
                           dy - BACK_INSET - THICKNESS_1 - saw_dy,
                           THICKNESS_0))
    saw_blade = BRepPrimAPI_MakeCylinder(SAW_RADIUS, THICKNESS_0).Shape()
    if is_left:
        saw_blade_x = THICKNESS_0 + SAW_RADIUS - SEPARATOR_NOTCH_DEPTH
    else:
        saw_blade_x = -SAW_RADIUS + SEPARATOR_NOTCH_DEPTH
    _move(saw_blade, saw_blade_x, dy - THICKNESS_0 - saw_dy,
          separator_offset - THICKNESS_0)
    side = _cut(side, saw_blade)
    return side

def _cut_side_back_notch(side, dy, dz, is_left):
    x = THICKNESS_0 - BACK_NOTCH_DEPTH if is_left else 0
    return _cut(
        side,
        _box(_pnt(x, dy - BACK_INSET - THICKNESS_1, 0),
             BACK_NOTCH_DEPTH, THICKNESS_1, dz))

def _make_topbottom(dx, dy, dz, is_top):
    panel = _box(dx, dy, THICKNESS_0)
    panel = _cut_topbottom_fingers(panel, dy, 0)
    panel = _cut_topbottom_fingers(panel, dy, dx - THICKNESS_0)
    panel = _cut_topbottom_back_notch(panel, dy, dx, is_top)
    if is_top:
        _move(panel, 0, 0, dz - THICKNESS_0)
    return panel

def _cut_topbottom_fingers(panel, dy, x):
    offset = dy - BACK_SPACE - FINGER_WIDTH
    while offset > -FINGER_WIDTH:
        panel = _cut(panel, _box(_pnt(x, offset, 0), THICKNESS_0, FINGER_WIDTH, THICKNESS_0))
        offset -= FINGER_WIDTH * 2
    return panel

def _cut_topbottom_back_notch(panel, dy, dx, is_top):
    z = 0 if is_top else THICKNESS_0 - BACK_NOTCH_DEPTH
    return _cut(
        panel,
        _box(_pnt(0, dy - BACK_INSET - THICKNESS_1, z),
             dx, THICKNESS_1, BACK_NOTCH_DEPTH))

def _make_back(dx, dy, dz):
    return _box(_pnt(THICKNESS_0 - BACK_NOTCH_DEPTH,
                     dy - BACK_INSET - THICKNESS_1,
                     THICKNESS_0 - BACK_NOTCH_DEPTH),
                dx - THICKNESS_0 * 2 + BACK_NOTCH_DEPTH * 2,
                THICKNESS_1,
                dz - THICKNESS_0 * 2 + BACK_NOTCH_DEPTH * 2)

def _make_separator(dx, dy, offset):
    saw_dy = math.sqrt(2 * SAW_RADIUS * SEPARATOR_NOTCH_DEPTH -
                       math.pow(SEPARATOR_NOTCH_DEPTH, 2))
    return _box(
        _pnt(THICKNESS_0 - SEPARATOR_NOTCH_DEPTH, 0, offset - THICKNESS_0),
        dx - THICKNESS_0 * 2 + SEPARATOR_NOTCH_DEPTH * 2,
        dy - BACK_INSET - THICKNESS_1 - saw_dy,
        THICKNESS_0)

def _move(shape, x, y, z):
    tr = gp.gp_Trsf()
    tr.SetTranslation(gp.gp_Vec(x, y, z))
    loc = TopLoc.TopLoc_Location(tr)
    shape.Move(loc)
