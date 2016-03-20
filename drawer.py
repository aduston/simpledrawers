import math
from OCC import gp, TopLoc
from OCC.gp import gp_Pnt
from OCC.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.TopoDS import TopoDS_Builder, TopoDS_Compound
from constants import THICKNESS_0, THICKNESS_1

FINGER_WIDTH = 0.8
BOTTOM_SPACE = 1.0
BOTTOM_INSET = 0.3
NOTCH_DEPTH = THICKNESS_0 / 2.0

_box = lambda *args: BRepPrimAPI_MakeBox(*args).Shape()
_cut = lambda *args: BRepAlgoAPI_Cut(*args).Shape()
_pnt = gp_Pnt

def make_drawer(dx, dy, dz):
    pieces = [
        _make_side(dx, dy, dz, True),
        _make_side(dx, dy, dz, False),
        _make_end(dx, dy, dz, True),
        _make_end(dx, dy, dz, False),
        _make_bottom(dx, dy)]

    builder = TopoDS_Builder()
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)
    for piece in pieces:
        builder.Add(compound, piece)
    return compound

def _make_bottom(dx, dy):
    bottom = _box(dx - THICKNESS_0 * 2 + NOTCH_DEPTH * 2,
                  dy - THICKNESS_0 * 2 + NOTCH_DEPTH * 2,
                  THICKNESS_1)
    _move(bottom, THICKNESS_0 - NOTCH_DEPTH, THICKNESS_0 - NOTCH_DEPTH, BOTTOM_INSET)
    return bottom

def _make_end(dx, dy, dz, is_front):
    end = _box(dx, THICKNESS_0, dz)
    end = _cut_end_fingers(end, 0, dz)
    end = _cut_end_fingers(end, dx - THICKNESS_0, dz)
    end = _cut_end_bottom_notch(end, dx, is_front)
    if is_front:
        end = _cut_finger_notch(end, dx, dz)
    if not is_front:
        _move(end, 0, dy - THICKNESS_0, 0)
    return end

def _cut_finger_notch(front, dx, dz):
    finger_width = 2.0
    finger_height = 1.0
    front = _cut(front, _box(_pnt(dx / 2. - finger_width / 2., 0, dz - finger_height),
                             finger_width, THICKNESS_0, finger_height))
    cyl = BRepPrimAPI_MakeCylinder(finger_width / 2.0, THICKNESS_0).Shape()
    tr = gp.gp_Trsf()
    tr.SetRotation(gp.gp_Ax1(gp.gp_Pnt(0, 0, 0), gp.gp_Dir(1, 0, 0)), math.pi / 2.0)
    tr2 = gp.gp_Trsf()
    tr2.SetTranslation(gp.gp_Vec(dx / 2., THICKNESS_0, dz - finger_height))
    tr2.Multiply(tr)
    cyl = BRepBuilderAPI_Transform(cyl, tr2, True).Shape()
    front = _cut(front, cyl)
    return front

def _cut_end_fingers(end, x, dz):
    offset = BOTTOM_SPACE
    while offset < dz:
        end = _cut(end, _box(_pnt(x, 0, offset), THICKNESS_0, THICKNESS_0, FINGER_WIDTH))
        offset += FINGER_WIDTH * 2
    return end

def _move(shape, x, y, z):
    tr = gp.gp_Trsf()
    tr.SetTranslation(gp.gp_Vec(x, y, z))
    loc = TopLoc.TopLoc_Location(tr)
    shape.Move(loc)
    
def _make_side(dx, dy, dz, is_left_side):
    side = _box(THICKNESS_0, dy, dz)
    side = _cut_side_fingers(side, 0, dz)
    side = _cut_side_fingers(side, dy - THICKNESS_0, dz)
    side = _cut_side_bottom_notch(side, dy, is_left_side)
    if not is_left_side:
        _move(side, dx - THICKNESS_0, 0, 0)
    return side

def _cut_side_fingers(side, y, dz):
    side = _cut(side, _box(_pnt(0, y, 0),
                           THICKNESS_0, THICKNESS_0, BOTTOM_SPACE))
    offset = BOTTOM_SPACE + FINGER_WIDTH
    while offset < dz:
        side = _cut(side, _box(_pnt(0, y, offset),
                               THICKNESS_0, THICKNESS_0, FINGER_WIDTH))
        offset += FINGER_WIDTH * 2
    return side

def _cut_side_bottom_notch(side, dy, is_left_side):
    x = NOTCH_DEPTH if is_left_side else 0.0
    return _cut(side, _box(_pnt(x, 0, BOTTOM_INSET), NOTCH_DEPTH, dy, THICKNESS_1))

def _cut_end_bottom_notch(end, dx, is_front):
    y = NOTCH_DEPTH if is_front else 0.0
    return _cut(end, _box(_pnt(0, y, BOTTOM_INSET), dx, NOTCH_DEPTH, THICKNESS_1))
