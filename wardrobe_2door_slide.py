# wardrobe_2door_slide.py
import math
from typing import Dict, List, Tuple
import pandas as pd
import streamlit as st

DEFAULTS = {
    # construction
    "wood_thick": 18.0,       # carcass core (MR/HDHMR) thickness
    "inside_lam": 0.8,        # laminate on inner faces
    "outside_lam": 2.0,       # laminate on outer faces
    "back_thick": 6.0,        # back board
    "plinth": 100.0,          # skirting height
    "groove": 7.0,            # groove depth for back/shelves
    "side_outside": True,     # sides outside top/bottom

    # storage
    "shelves": 4,
    "drawers": 2,
    "draw_height": 150.0,
    "have_center_partition": True,  # typical for long wardrobes

    # sliding hardware
    "door_thick": 18.0,       # shutter board
    "overlap": 60.0,          # total panel overlap (distributed across leaves)
    "top_track_h": 80.0,      # top track + clearance
    "bottom_track_h": 45.0,   # bottom track + clearance
    "running_clear": 10.0,    # extra running play in height
    "stile_side_clear": 3.0,  # side clearance between leaf & gable (per side)

    # back splitting
    "back_split_max": 1160.0,
}

# ---------------- UI (all vertical, one-by-one) ----------------
def form_type1(prefill: Dict=None, button_label: str="Add"):
    if prefill is None:
        prefill = {}

    st.subheader("2-Door Sliding Wardrobe – Inputs")


    height = st.number_input("Height (mm)", 1000.0, 4200.0,
                             value=float(prefill.get("height", 2075.0)), step=1.0, key="s_height")
    
    length = st.number_input("Width (mm)", 1200.0, 5000.0,
                             value=float(prefill.get("length", 2350.0)), step=1.0, key="s_len")
    
    depth  = st.number_input("Depth (mm)", 450.0, 800.0,
                             value=float(prefill.get("depth", 600.0)), step=1.0, key="s_depth")

    shelves = st.number_input("Horizontal Shelves (qty)", 0, 16,
                              value=int(prefill.get("shelves", DEFAULTS["shelves"])), step=1, key="s_shelves")

    drawers = st.number_input("Drawers (qty)", 0, 8,
                              value=int(prefill.get("drawers", DEFAULTS["drawers"])), step=1, key="s_drawers")

    draw_height = st.number_input("Drawer Height (mm)", 100.0, 525.0,
                                 value=float(prefill.get("draw_height", DEFAULTS["draw_height"])), step=1.0, key="s_draw_h")

    # NEW: thicknesses split as core + inside/outside laminates
    wood_thick = st.number_input("Wood Thickness (mm)", 12.0, 25.0,
                                 value=float(prefill.get("wood_thick", DEFAULTS["wood_thick"])), step=0.5, key="s_core")
    inside_lam = st.number_input("Inside Laminate Thickness (mm)", 0.0, 2.0,
                                 value=float(prefill.get("inside_lam", DEFAULTS["inside_lam"])), step=0.1, key="s_inlam")
    outside_lam = st.number_input("Outside Laminate Thickness (mm)", 0.0, 2.0,
                                  value=float(prefill.get("outside_lam", DEFAULTS["outside_lam"])), step=0.1, key="s_outlam")

    back_thick = st.number_input("Back Thickness (mm)", 3.0, 9.0,
                                 value=float(prefill.get("back_thick", DEFAULTS["back_thick"])), step=0.5, key="s_bt")

    plinth = st.number_input("Skirting / Plinth (mm)", 0.0, 200.0,
                             value=float(prefill.get("plinth", DEFAULTS["plinth"])), step=1.0, key="s_plinth")

    groove = st.number_input("Groove Allowance (mm)", 0.0, 10.0,
                             value=float(prefill.get("groove", DEFAULTS["groove"])), step=0.5, key="s_groove")

    side_outside = st.selectbox("Assembly preference",
                                ["Side panels outside", "Top/Bottom outside"],
                                index=0 if prefill.get("side_outside", DEFAULTS["side_outside"]) else 1,
                                key="s_side_out").startswith("Side")

    # have_center_partition = st.checkbox("Center Partition",
    #                                     value=bool(prefill.get("have_center_partition", DEFAULTS["have_center_partition"])),
    #                                     key="s_has_part")

    # top_track_h = st.number_input("Top Track Height (mm)", 40.0, 120.0,
    #                               value=float(prefill.get("top_track_h", DEFAULTS["top_track_h"])),
    #                               step=1.0, key="s_ttrack")

    # bottom_track_h = st.number_input("Bottom Track Height (mm)", 20.0, 120.0,
    #                                  value=float(prefill.get("bottom_track_h", DEFAULTS["bottom_track_h"])),
    #                                  step=1.0, key="s_btrack")

    # running_clear = st.number_input("Running Clearance (mm)", 0.0, 20.0,
    #                                 value=float(prefill.get("running_clear", DEFAULTS["running_clear"])),
    #                                 step=0.5, key="s_runclr")

    # door_thick = st.number_input("Door Thickness (mm)", 12.0, 25.0,
    #                              value=float(prefill.get("door_thick", DEFAULTS["door_thick"])), step=0.5, key="s_dth")

    # overlap = st.number_input("Leaf Overlap (mm)", 20.0, 120.0,
    #                           value=float(prefill.get("overlap", DEFAULTS["overlap"])),
    #                           step=1.0, key="s_overlap")

    # stile_side_clear = st.number_input("Side Clearance (per side, mm)", 0.0, 10.0,
    #                                    value=float(prefill.get("stile_side_clear", DEFAULTS["stile_side_clear"])),
    #                                    step=0.5, key="s_sideclr")

    submitted = st.form_submit_button(button_label)

    data = dict(
        length=length, height=height, depth=depth,
        wood_thick=wood_thick, inside_lam=inside_lam, outside_lam=outside_lam,
        back_thick=back_thick, plinth=plinth, groove=groove,
        side_outside=side_outside, shelves=shelves, drawers=drawers,
        draw_height=draw_height
        # have_center_partition=have_center_partition,
        # top_track_h=top_track_h, bottom_track_h=bottom_track_h, running_clear=running_clear,
        # door_thick=door_thick, overlap=overlap, stile_side_clear=stile_side_clear,
        # back_split_max=float(prefill.get("back_split_max", DEFAULTS["back_split_max"]))
    )
    return submitted, data

# --------------- helpers ---------------
def _fmt(name: str, qty: int, h: float, w: float, notes: str="") -> str:
    h = round(h, 1); w = round(w, 1)
    return f"{name}: {qty} pcs — {h} × {w} mm" + (f" — {notes}" if notes else "")

def _row(name, qty, h, w, notes=""):
    return dict(item=name, qty=int(qty), height_mm=round(h, 1), width_mm=round(w, 1), notes=notes)

def _split_back(length: float, back_split_max: float):
    n = max(1, math.ceil(length / back_split_max))
    each = length / n
    return n, each

# --------------- calculations ---------------
def calc_type1(d: Dict) -> List[str]:
    L = float(d["length"])
    H = float(d["height"])
    D = float(d["depth"])
    WOOD = float(d["wood_thick"])
    IN = float(d["inside_lam"])
    OUT = float(d["outside_lam"])
    B = float(d["back_thick"])
    P = float(d["plinth"])
    groove = float(d["groove"])
    side_outside = bool(d["side_outside"])
    shelves = int(d["shelves"])
    drawers = int(d["drawers"])
    drawer_height = float(d["draw_height"])
    # have_center_partition = bool(d["have_center_partition"])
    # top_track_h = float(d["top_track_h"])
    # bottom_track_h = float(d["bottom_track_h"])
    # running_clear = float(d["running_clear"])
    # door_thick = float(d["door_thick"])
    # overlap = float(d["overlap"])
    # side_clear = float(d["stile_side_clear"])
    # back_split_max = float(d["back_split_max"])

    WOOD_IN = WOOD + IN  #Wood + Inside laminate
    WOOD_OUT = WOOD + OUT  #Wood + Inside laminate
    WOOD_IN_OUT = WOOD + IN + OUT  #Wood + both laminates

    out: List[str] = []

    # --- carcass ---
    side_h = H - OUT
    side_w = D - OUT
    out.append(_fmt("Left Panel", 1, side_h, side_w, f"{groove}mm - groove to back;"))
    out.append(_fmt("Right Panel", 1, side_h, side_w, f"{groove}mm - groove to back;"))

    # Top/Bottom length is between **inside faces of sides**
    tb_len = (L - 2*WOOD_OUT) if side_outside else L
    tb_w   = D - OUT
    out.append(_fmt("Top Panel", 1, tb_len, tb_w, f"{WOOD}mm core; groove to back"))
    out.append(_fmt("Bottom Panel", 1, tb_len, tb_w, f"{WOOD}mm core; groove to back"))

    # Back panel(s): sit in grooves; height reduced by grooves on top/bottom
    back_h = H - P - (2*(WOOD_IN - groove))
    back_l = (L - 2*WOOD_OUT - WOOD + 4*groove)/2
    out.append(_fmt(f"Back ({int(B)}mm)", 2, back_h, back_l, f"{int(B)}mm"))


    # Center partition (meets top/bottom **inside faces**)
    #if have_center_partition:
    part_h = H - P - 2*WOOD_OUT
    part_w = D - B - 5*WOOD
    out.append(_fmt("Center Partition", 1, part_h, part_w, f"{WOOD}mm core"))

    door_h = H - P - 3*WOOD_IN_OUT
    door_w = (L + WOOD)/2
    out.append(_fmt("Doors", 2, door_h, door_w, f"{WOOD}mm core"))

    # Fixed shelf across carcass (between inside faces / includes partition allowance)
    shelf_len = (L - 3*WOOD_OUT)/2
    shelf_w   = D - B - 5*WOOD
    out.append(_fmt("Horizontal Shelf", shelves, shelf_len, shelf_w, f"{WOOD}mm core"))

    # # Adjustable shelves (per bay)
    # if shelves > 0:
    #     bays = 2 if have_center_partition else 1
    #     # Each bay length inside = internal opening per bay minus the partition inner-face thickness at one side
    #     shelf_len = tb_len / bays - (WOOD_IN if have_center_partition else 0)
    #     shelf_w = D - B
    #     out.append(_fmt("Adjustable Shelf", shelves, shelf_len, shelf_w, f"{WOOD}mm core"))

    if drawers > 0:
        draw_s_h = drawer_height - 2*WOOD_IN
        draw_s_d = D - B - 5*WOOD
        draw_f_h = drawer_height - 2*WOOD_IN
        draw_f_w = (L - 26*WOOD)/4
        draw_b_h = drawer_height - 2*WOOD_IN
        draw_b_w = (L - 26*WOOD)/4
        draw_bo_w = (L -  25*WOOD)/4
        draw_bo_d = D - B - 5*WOOD
        draw_fa_h = drawer_height - WOOD
        draw_fa_w = (L - 12*WOOD_IN)/4
        out.append(_fmt("Drawer Side Panel", drawers*2, draw_s_h, draw_s_d, f"{WOOD}mm; groove"))
        out.append(_fmt("Drawer Front Panel", drawers, draw_f_h, draw_f_w, f"{WOOD}mm"))
        out.append(_fmt("Drawer Back Panel", drawers, draw_b_h, draw_b_w, f"{WOOD}mm"))
        out.append(_fmt(f"Drawer Bottom ({int(B)}mm)", drawers, draw_bo_w, draw_bo_d, f"{int(B)}mm"))
        out.append(_fmt("Drawer Fascia", drawers, draw_fa_h, draw_fa_w, "exposed"))
        out.append(_fmt("Drawer Dummy", drawers*2, draw_s_h, draw_s_d,))


    return out


def get_cutlist_df(d: Dict) -> pd.DataFrame:
    L = float(d["length"])
    H = float(d["height"])
    D = float(d["depth"])
    WOOD = float(d["wood_thick"])
    IN = float(d["inside_lam"])
    OUT = float(d["outside_lam"])
    B = float(d["back_thick"])
    P = float(d["plinth"])
    groove = float(d["groove"])
    side_outside = bool(d["side_outside"])
    shelves = int(d["shelves"])
    drawers = int(d["drawers"])
    drawer_height = float(d["draw_height"])

    rows = []

    WOOD_IN = WOOD + IN  #Wood + Inside laminate
    WOOD_OUT = WOOD + OUT  #Wood + Inside laminate
    WOOD_IN_OUT = WOOD + IN + OUT  #Wood + both laminates

    # --- carcass ---
    side_h = H - OUT
    side_w = D - OUT
    rows.append(_row("Left Panel", 1, side_h, side_w, f"{groove}mm - groove to back;"))
    rows.append(_row("Right Panel", 1, side_h, side_w, f"{groove}mm - groove to back;"))

    # Top/Bottom length is between **inside faces of sides**
    tb_len = (L - 2*WOOD_OUT) if side_outside else L
    tb_w   = D - OUT
    rows.append(_row("Top Panel", 1, tb_len, tb_w, f"{WOOD}mm core; groove to back"))
    rows.append(_row("Bottom Panel", 1, tb_len, tb_w, f"{WOOD}mm core; groove to back"))

    # Back panel(s): sit in grooves; height reduced by grooves on top/bottom
    back_h = H - P - (2*(WOOD_IN - groove))
    back_l = (L - 2*WOOD_OUT - WOOD + 4*groove)/2
    rows.append(_row(f"Back ({int(B)}mm)", 2, back_h, back_l, f"{int(B)}mm"))


    # Center partition (meets top/bottom **inside faces**)
    #if have_center_partition:
    part_h = H - P - 2*WOOD_OUT
    part_w = D - B - 5*WOOD
    rows.append(_row("Center Partition", 1, part_h, part_w, f"{WOOD}mm core"))

    door_h = H - P - 3*WOOD_IN_OUT
    door_w = (L + WOOD)/2
    rows.append(_row("Doors", 2, door_h, door_w, f"{WOOD}mm core"))

    # Fixed shelf across carcass (between inside faces / includes partition allowance)
    shelf_len = (L - 3*WOOD_OUT)/2
    shelf_w   = D - B - 5*WOOD
    rows.append(_row("Horizontal Shelf", shelves, shelf_len, shelf_w, f"{WOOD}mm core"))

    # # Adjustable shelves (per bay)
    # if shelves > 0:
    #     bays = 2 if have_center_partition else 1
    #     # Each bay length inside = internal opening per bay minus the partition inner-face thickness at one side
    #     shelf_len = tb_len / bays - (WOOD_IN if have_center_partition else 0)
    #     shelf_w = D - B
    #     out.append(_fmt("Adjustable Shelf", shelves, shelf_len, shelf_w, f"{WOOD}mm core"))

    if drawers > 0:
        draw_s_h = drawer_height - 2*WOOD_IN
        draw_s_d = D - B - 5*WOOD
        draw_f_h = drawer_height - 2*WOOD_IN
        draw_f_w = (L - 26*WOOD)/4
        draw_b_h = drawer_height - 2*WOOD_IN
        draw_b_w = (L - 26*WOOD)/4
        draw_bo_w = (L -  25*WOOD)/4
        draw_bo_d = D - B - 5*WOOD
        draw_fa_h = drawer_height - WOOD
        draw_fa_w = (L - 12*WOOD_IN)/4
        rows.append(_row("Drawer Side Panel", drawers*2, draw_s_h, draw_s_d, f"{WOOD}mm; groove"))
        rows.append(_row("Drawer Front Panel", drawers, draw_f_h, draw_f_w, f"{WOOD}mm"))
        rows.append(_row("Drawer Back Panel", drawers, draw_b_h, draw_b_w, f"{WOOD}mm"))
        rows.append(_row(f"Drawer Bottom ({int(B)}mm)", drawers, draw_bo_w, draw_bo_d, f"{int(B)}mm"))
        rows.append(_row("Drawer Fascia", drawers, draw_fa_h, draw_fa_w, "exposed"))
        rows.append(_row("Drawer Dummy", drawers*2, draw_s_h, draw_s_d,))


#     # carcass
#     side_h = H - P
#     side_w = D
#     rows.append(_row("Left Panel", 1, side_h, side_w, f"{WOOD}mm core;"))
#     rows.append(_row("Right Panel", 1, side_h, side_w, f"{WOOD}mm core;"))

#     tb_len = (L - 2*WOOD_IN) if side_outside else L
#     tb_w   = D
#     rows.append(_row("Top Panel", 1, tb_len, tb_w, f"{WOOD}mm core; groove to back"))
#     rows.append(_row("Bottom Panel", 1, tb_len, tb_w, f"{WOOD}mm core; groove to back"))

#     back_h = H - P - (2*groove)
#     back_l = L - 2*WOOD_OUT - WOOD + 2*groove
#     rows.append(_row(f"Back ({int(B)}mm)", 2, back_h, back_l, f"{int(B)}mm"))

#     if have_center_partition:
#         rows.append(_row("Center Partition", 1, H - P - WOOD - groove, D - B, f"{WOOD}mm core"))

#     rows.append(_row("Fixed Shelf", 1, tb_len, D - B, f"{WOOD}mm core"))

#     if shelves > 0:
#         bays = 2 if have_center_partition else 1
#         shelf_len = tb_len / bays - (WOOD_IN if have_center_partition else 0)
#         rows.append(_row("Adjustable Shelf", shelves, shelf_len, D - B, f"{WOOD}mm core"))

#     if drawers > 0:
#         bay_w_clear = (tb_len / (2 if have_center_partition else 1)) - 2*WOOD_IN
#         bay_d_clear = D - B - WOOD
#         box_h = 174.0 if H <= 2600 else 138.0
#         rows.append(_row("Drawer Side Panel", drawers*2, box_h-2, bay_d_clear, f"{WOOD}mm; groove"))
#         rows.append(_row("Drawer Front Panel", drawers, box_h-2, bay_w_clear, f"{WOOD}mm"))
#         rows.append(_row("Drawer Back Panel", drawers, box_h-2, bay_w_clear, f"{WOOD}mm"))
#         rows.append(_row(f"Drawer Bottom ({int(B)}mm)", drawers, bay_d_clear, bay_w_clear, f"{int(B)}mm"))
#         rows.append(_row("Drawer Fascia", drawers, (box_h-2)+56, bay_w_clear+72, "exposed"))

#     rows.append(_row("Skirting (front)", 1, 98.0, tb_len, f"{WOOD}mm"))
#     rows.append(_row("Side Dummy Trim", 1, H - P, 40.0, f"{WOOD}mm"))

#     opening_w = tb_len
#     leaf_w = (opening_w + overlap) / 2.0 - side_clear
#     leaf_h = H - P - top_track_h - bottom_track_h - running_clear
#     rows.append(_row(f"Sliding Shutter (leaf, {int(door_thick)}mm)", 2, leaf_h, leaf_w, f"{int(door_thick)}mm"))

    return pd.DataFrame(rows)
