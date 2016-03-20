from OCC import gp, TopLoc
from OCC.gp import gp_Pnt
from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.TopoDS import TopoDS_Builder, TopoDS_Compound
from constants import THICKNESS_0, THICKNESS_1

_box = lambda *args: BRepPrimAPI_MakeBox(*args).Shape()
_cut = lambda *args: BRepAlgoAPI_Cut(*args).Shape()
_pnt = gp_Pnt

FINGER_WIDTH = 0.8
BOTTOM_SPACE = 1.0
BOTTOM_INSET = 0.3

def make_drawer(dx, dy, dz):
    side_0 = _make_side(dy, dz, True)
    side_1 = _make_side(dy, dz, False)
    _move(side_1, dx - THICKNESS_0, 0, 0)

    builder = TopoDS_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    builder.Add(compound, side_0)
    builder.Add(compound, side_1)
    return compound
    
    # front = _make_front(dx, dz)
    # back = _make_front(dx, dz)
    # bottom = _make_bottom(dx, dy)
    # return _assemble_drawer(side_0, side_1, front, back, bottom, dx, dy)

def _move(shape, x, y, z):
    tr = gp.gp_Trsf()
    tr.SetTranslation(gp.gp_Vec(x, y, z))
    loc = TopLoc.TopLoc_Location(tr)
    shape.Move(loc)
    
def _make_side(dy, dz, is_left_side):
    side = _box(THICKNESS_0, dy, dz)
    side = _cut_fingers(side, 0, dz)
    side = _cut_fingers(side, dy - THICKNESS_0, dz)
    return _cut_bottom_notch(side, dy, is_left_side)

def _cut_fingers(side, y, dz):
    side = _cut(side, _box(_pnt(0, y, 0),
                           THICKNESS_0, THICKNESS_0, BOTTOM_SPACE))
    offset = BOTTOM_SPACE + FINGER_WIDTH
    while offset < dz:
        side = _cut(side, _box(_pnt(0, y, offset),
                               THICKNESS_0, THICKNESS_0, FINGER_WIDTH))
        offset += FINGER_WIDTH * 2
    return side

def _cut_bottom_notch(side, dy, is_left_side):
    notch_depth = THICKNESS_0 / 2.0
    x = notch_depth if is_left_side else 0.0
    return _cut(side, _box(_pnt(x, 0, BOTTOM_INSET), notch_depth, dy, THICKNESS_1))
