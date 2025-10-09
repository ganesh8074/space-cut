# ------- keep everything above as-is, then REPLACE calc_type1() and get_cutlist_df() -------
import math
from typing import Dict, List, Tuple
import pandas as pd
import streamlit as st


DEFAULTS = {
    # construction
    "wood_thick": 18.0,       # carcass core (MR/HDHMR) thickness
    "inside_lam": 1.0,        # laminate on inner faces
    "outside_lam": 1.0,       # laminate on outer faces
    "back_thick": 6.0,        # back board
    "plinth": 100.0,          # skirting height
    "groove": 7.0,            # groove depth for back/shelves
    "side_outside": True,     # sides outside top/bottom

    # storage
    "shelves": 4,
    "l_drawers": 2,
    "r_drawers": 2,
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
    #"back_split_max": 1160.0,
    "part_type_left": "SVD",  # partition type: S, SV, SVD, SVD2, SD, SD
    "part_type_right": "SVD",  # partition type: S, SV, SVD, SVD2, SD, SD
    "ver_shelf_height": 100.0, # vertical shelf height
}

# ---------------- UI (all vertical, one-by-one) ----------------
def form_type1(prefill: Dict=None, button_label: str="Add"):
    if prefill is None:
        prefill = {}

    st.subheader("2-Door Wardrobe – Inputs")


    height = st.number_input("Height (mm)", 1000.0, 4200.0,
                             value=float(prefill.get("height", 2075.0)), step=1.0, key="s_height")
    
    length = st.number_input("Width (mm)", 1200.0, 5000.0,
                             value=float(prefill.get("length", 2350.0)), step=1.0, key="s_len")
    
    depth  = st.number_input("Depth (mm)", 450.0, 800.0,
                             value=float(prefill.get("depth", 600.0)), step=1.0, key="s_depth")

    # Partition type selectors for both sides
    part_type_left = st.selectbox("Left Partition Type",
        ["S", "SV", "SVD", "SVD2",  "SD", "SD2"],
        index=3 if prefill.get("part_type_left", "SV") in ["S", "SV", "SVD", "SVD2", "SD", "SD2"] else 0,
        key="s_part_type_left"
    )
    part_type_right = st.selectbox("Right Partition Type",
        ["S", "SV", "SVD", "SVD2",  "SD", "SD2"],
        index=2 if prefill.get("part_type_right", "SV") in ["S", "SV", "SVD", "SVD2", "SD", "SD2"] else 0,
        key="s_part_type_right"
    )

    shelves = st.number_input("Horizontal Shelves (qty)", 0, 16,
                              value=int(prefill.get("shelves", DEFAULTS["shelves"])), step=1, key="s_shelves")

    ver_shelf_height = st.number_input("Vertical Shlef Total Height (mm)", 10.0, 3000.0,
                                    value=float(prefill.get("ver_shelf_height", DEFAULTS["ver_shelf_height"])), step=1.0, key="s_dver_shelf_h")

    l_drawers = st.number_input("Left Part Drawers (qty)", 0, 8,
                              value=int(prefill.get("drawers", DEFAULTS["l_drawers"])), step=1, key="s_r_drawers")
    r_drawers = st.number_input("Right Part Drawers (qty)", 0, 8,
                              value=int(prefill.get("drawers", DEFAULTS["r_drawers"])), step=1, key="s_l_drawers")

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
        side_outside=side_outside, shelves=shelves, l_drawers=l_drawers, r_drawers=r_drawers,
        draw_height=draw_height,part_type_left=part_type_left, part_type_right=part_type_right,
        ver_shelf_height=ver_shelf_height,
        # have_center_partition=have_center_partition,
        # top_track_h=top_track_h, bottom_track_h=bottom_track_h, running_clear=running_clear,
        # door_thick=door_thick, overlap=overlap, stile_side_clear=stile_side_clear,
        # back_split_max=float(prefill.get("back_split_max", DEFAULTS["back_split_max"]))
    )
    return submitted, data
# ---- REPLACE calc_type1() and get_cutlist_df() in wardrobe_2door_slide.py ----

def _dims(h, w):
    # compact dimension string (no qty, mm implied)
    return f"{round(h,1)} × {round(w,1)}"

def _dims_2(h, w, qty):
    # compact dimension string with qty (mm implied)
    return f"{round(h,1)} × {round(w,1)} = {qty} qty"

def calc_type1(d: Dict):
    """
    Keep for backward compatibility, but don't emit bullet strings.
    The main app will render the DataFrame returned by get_cutlist_df().
    """
    return []  # we want the table, not bullets

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
    l_drawers = int(d["l_drawers"])
    r_drawers = int(d["r_drawers"])
    drawer_height = float(d["draw_height"])
    part_type_left = d.get("part_type_left", DEFAULTS["part_type_left"])
    part_type_right = d.get("part_type_right", DEFAULTS["part_type_right"])
    ver_shelf_height = float(d["ver_shelf_height"])

    rows = []

    WOOD_IN = WOOD + IN
    WOOD_OUT = WOOD + OUT
    WOOD_IN_OUT = WOOD + IN + OUT

    # sides
    side_h = H - OUT
    side_w = D - OUT
    for label in ["Left Panel", "Right Panel"]:
        rows.append({
            "Cut piece name": label,
            "Wood": _dims(side_h, side_w),
            "Colour laminate": _dims(side_h, side_w),   # outside
            "White laminate": _dims(side_h, side_w),    # inside
            "Colour edge bidding": round(H + D, 1),
            "White edge bidding": round(D, 1),
        })

    # top / bottom
    tb_len = (L - 2*WOOD_IN_OUT - 2*IN) if side_outside else L
    tb_w   = D - OUT
    rows.append({
        "Cut piece name": "Top Panel",
        "Wood": _dims(tb_len, tb_w),
        "Colour laminate": _dims(tb_len, tb_w),
        "White laminate": _dims(tb_len, tb_w),
        "Colour edge bidding": round(tb_len + 2*IN, 1),
        "White edge bidding": round(2*D, 1),
    })
    rows.append({
        "Cut piece name": "Bottom Panel",
        "Wood": _dims(tb_len, tb_w),
        "Colour laminate": "",                      # as per your earlier list
        "White laminate": _dims(tb_len, tb_w),
        "Colour edge bidding": 0.0,
        "White edge bidding": round(2*D + tb_len + 2*IN, 1),   # white twice there
    })

    # back (in grooves)
    back_h = H - P - (2*(WOOD_IN - groove))
    back_l = (L - 3*WOOD + 4*groove)/2
    rows.append({
        "Cut piece name": f"Back ({int(B)}mm)",
        "Wood": _dims_2(back_h, back_l, 2),   # 2 pcs implied
        "Colour laminate": "",
        "White laminate": _dims_2(back_h, back_l, 4),
        "Colour edge bidding": 0.0,
        "White edge bidding": 0.0,
    })


    # center partition
    part_h = H - P - WOOD_IN_OUT
    part_w = D - B - 50
    rows.append({
        "Cut piece name": "Center Partition",
        "Wood": _dims(part_h, part_w),
        "Colour laminate": "",
        "White laminate": _dims_2(part_h, part_w, 2),
        "Colour edge bidding": 0.0,
        "White edge bidding": round(2*part_h + 2*part_w, 1),
    })

    # doors
    door_h = H - P - WOOD_IN_OUT
    door_w = (L - 4*OUT)/2
    rows.append({
        "Cut piece name": "Doors",
        "Wood": _dims_2(door_h, door_w, 2),
        "Colour laminate": _dims_2(door_h, door_w,2),
        "White laminate": _dims_2(door_h, door_w,2),
        "Colour edge bidding": round(4*door_h + 4*door_w, 1),
        "White edge bidding": 0.0,
    })

    # bottom skirting
    rows.append({
        "Cut piece name": "Bottom SKT",
        "Wood": _dims(P - OUT, L - 2*OUT),
        "Colour laminate": _dims(P - OUT, L - 2*OUT),
        "White laminate": "",
        "Colour edge bidding": round(2*P + L, 1),
        "White edge bidding": "",
    })

    # shelves
    shelf_len = (L - 3*WOOD_IN_OUT)/2
    if shelves > 0:
        total_shelfs = shelves
        rows.append({
            "Cut piece name": "Horizontal Shelf",
            "Wood": _dims_2(shelf_len, part_w, total_shelfs),            # per shelf
            "Colour laminate": "",
            "White laminate": _dims_2(shelf_len, part_w, 2*(total_shelfs)),  # per face (compact)
            "Colour edge bidding": 0.0,
            "White edge bidding": round(2*total_shelfs*shelf_len + 2*total_shelfs*part_w, 1),
        })

        l_sing_draw = 0
        r_sing_draw = 0
        l_doub_draw = 0
        r_doub_draw = 0


    if part_type_left in ["S"]:
        l_drawers = 0
    elif part_type_left in ["SV"]:
        l_drawers = 0
    elif part_type_left in ["SVD2"]:
        l_doub_draw = l_drawers - l_drawers % 2
        l_sing_draw = l_drawers % 2
    elif part_type_left in ["SD2"]:
        l_doub_draw = l_drawers - l_drawers % 2
        l_sing_draw = l_drawers % 2
    elif part_type_left in ["SD"]:
        l_doub_draw = 0
        l_sing_draw = l_drawers
    elif part_type_left in ["SVD"]:
        l_doub_draw = 0
        l_sing_draw = l_drawers

    if l_sing_draw > 0:
        draw_s_h = drawer_height - 2*WOOD_IN
        draw_s_d = D - B - 3*WOOD
        draw_f_h = drawer_height - 2*WOOD
        draw_f_w = (L - 4*WOOD)
        draw_b_h = drawer_height - 2*WOOD_IN
        draw_b_w = (L - 4*WOOD)
        draw_bo_w = (L -  3*WOOD)
        draw_bo_d = D - B - 4*WOOD
        draw_fa_h = drawer_height - WOOD
        draw_fa_w = (L - WOOD_IN)

        rows.append({
            "Cut piece name": "Left Single Drawer Side Panel ",
            "Wood": _dims_2(draw_s_h, draw_s_d, 2*l_sing_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_s_h, draw_s_d, 2*l_sing_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(4*l_sing_draw*draw_s_h + 4*l_sing_draw*draw_s_d, 1),
        })
        rows.append({
            "Cut piece name": "Left Single Drawer Front Panel",
            "Wood": _dims_2(draw_f_h, draw_f_w, l_sing_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_f_h, draw_f_w, l_sing_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(2*l_sing_draw*draw_f_h + 2*l_sing_draw*draw_f_w, 1),
        })
        rows.append({
            "Cut piece name": "Left Single Drawer Back Panel",
            "Wood": _dims_2(draw_b_h, draw_b_w, l_sing_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_b_h, draw_b_w, l_sing_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(2*l_sing_draw*draw_b_h + 2*l_sing_draw*draw_b_w, 1),
        })
        rows.append({
            "Cut piece name": f"Left Single Drawer Bottom ({int(B)}mm)",
            "Wood": _dims_2(draw_bo_w, draw_bo_d, l_sing_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_bo_w, draw_bo_d, l_sing_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": 0.0,
        })
        rows.append({
            "Cut piece name": "Left Single Drawer Fascia",
            "Wood": _dims_2(draw_fa_h, draw_fa_w, l_sing_draw),
            "Colour laminate": _dims_2(draw_fa_h, draw_fa_w, l_sing_draw),
            "White laminate": _dims_2(draw_fa_h, draw_fa_w, l_sing_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(2*l_sing_draw*draw_fa_h + 2*l_sing_draw*draw_fa_w, 1),
        })
        rows.append({
            "Cut piece name": "Left Single Drawer Dummy",
            "Wood": _dims_2(draw_s_h, draw_s_d, 2*l_sing_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_s_h, draw_s_d, 2*l_sing_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(4*l_sing_draw*draw_s_h + 4*l_sing_draw*draw_s_d, 1),
        })

    if l_doub_draw > 0:
        draw_s_h = drawer_height - 2*WOOD_IN
        draw_s_d = D - B - 3*WOOD
        draw_f_h = drawer_height - 2*WOOD
        draw_f_w = (L - 4*WOOD)/2
        draw_b_h = drawer_height - 2*WOOD_IN
        draw_b_w = (L - 4*WOOD)/2
        draw_bo_w = (L -  3*WOOD)/2
        draw_bo_d = D - B - 4*WOOD
        draw_fa_h = drawer_height - WOOD
        draw_fa_w = (L - WOOD_IN)/2

        rows.append({
            "Cut piece name": "Left Double Drawer Side Panel",
            "Wood": _dims_2(draw_s_h, draw_s_d, 2*l_doub_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_s_h, draw_s_d, 2*l_doub_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(4*l_doub_draw*draw_s_h + 4*l_doub_draw*draw_s_d, 1),
        })
        rows.append({
            "Cut piece name": "Left Double Drawer Front Panel",
            "Wood": _dims_2(draw_f_h, draw_f_w, l_doub_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_f_h, draw_f_w, l_doub_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(2*l_doub_draw*draw_f_h + 2*l_doub_draw*draw_f_w, 1),
        })
        rows.append({
            "Cut piece name": "Left Double Drawer Back Panel",
            "Wood": _dims_2(draw_b_h, draw_b_w, l_doub_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_b_h, draw_b_w, l_doub_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(2*l_doub_draw*draw_b_h + 2*l_doub_draw*draw_b_w, 1),
        })
        rows.append({
            "Cut piece name": f"Left Double Drawer Bottom ({int(B)}mm)",
            "Wood": _dims_2(draw_bo_w, draw_bo_d, l_doub_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_bo_w, draw_bo_d, l_doub_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": 0.0,
        })
        rows.append({
            "Cut piece name": "Left Double Drawer Fascia",
            "Wood": _dims_2(draw_fa_h, draw_fa_w, l_doub_draw),
            "Colour laminate": _dims_2(draw_fa_h, draw_fa_w, l_doub_draw),
            "White laminate": _dims_2(draw_fa_h, draw_fa_w, l_doub_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(2*l_doub_draw*draw_fa_h + 2*l_doub_draw*draw_fa_w, 1),
        })
        rows.append({
            "Cut piece name": "Left Double Drawer Dummy",
            "Wood": _dims_2(draw_s_h, draw_s_d, 2*l_doub_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_s_h, draw_s_d, 2*l_doub_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(4*l_doub_draw*draw_s_h + 4*l_doub_draw*draw_s_d, 1),
        })

#right side partition drawers
    if part_type_right in ["S"]:
        r_drawers = 0
    elif part_type_right in ["SV"]:
        r_drawers = 0
    elif part_type_right in ["SVD2"]:
        r_doub_draw = r_drawers - r_drawers % 2
        r_sing_draw = r_drawers % 2
    elif part_type_right in ["SD2"]:
        r_doub_draw = r_drawers - r_drawers % 2
        r_sing_draw = r_drawers % 2
    elif part_type_right in ["SD"]:
        r_doub_draw = 0
        r_sing_draw = r_drawers
    elif part_type_right in ["SVD"]:
        r_doub_draw = 0
        r_sing_draw = r_drawers

    if r_sing_draw > 0:
        draw_s_h = drawer_height - 2*WOOD_IN
        draw_s_d = D - B - 3*WOOD
        draw_f_h = drawer_height - 2*WOOD
        draw_f_w = (L - 4*WOOD)
        draw_b_h = drawer_height - 2*WOOD_IN
        draw_b_w = (L - 4*WOOD)
        draw_bo_w = (L -  3*WOOD)
        draw_bo_d = D - B - 4*WOOD
        draw_fa_h = drawer_height - WOOD
        draw_fa_w = (L - WOOD_IN)

        rows.append({
            "Cut piece name": "Right Single Drawer Side Panel ",
            "Wood": _dims_2(draw_s_h, draw_s_d, 2*r_sing_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_s_h, draw_s_d, 2*r_sing_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(4*r_sing_draw*draw_s_h + 4*r_sing_draw*draw_s_d, 1),
        })
        rows.append({
            "Cut piece name": "Right Single Drawer Front Panel",
            "Wood": _dims_2(draw_f_h, draw_f_w, r_sing_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_f_h, draw_f_w, r_sing_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(2*r_sing_draw*draw_f_h + 2*r_sing_draw*draw_f_w, 1),
        })
        rows.append({
            "Cut piece name": "Right Single Drawer Back Panel",
            "Wood": _dims_2(draw_b_h, draw_b_w, r_sing_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_b_h, draw_b_w, r_sing_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(2*r_sing_draw*draw_b_h + 2*r_sing_draw*draw_b_w, 1),
        })
        rows.append({
            "Cut piece name": f"Right Single Drawer Bottom ({int(B)}mm)",
            "Wood": _dims_2(draw_bo_w, draw_bo_d, r_sing_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_bo_w, draw_bo_d, r_sing_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": 0.0,
        })
        rows.append({
            "Cut piece name": "Right Single Drawer Fascia",
            "Wood": _dims_2(draw_fa_h, draw_fa_w, r_sing_draw),
            "Colour laminate": _dims_2(draw_fa_h, draw_fa_w, r_sing_draw),
            "White laminate": _dims_2(draw_fa_h, draw_fa_w, r_sing_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(2*r_sing_draw*draw_fa_h + 2*r_sing_draw*draw_fa_w, 1),
        })
        rows.append({
            "Cut piece name": "Right Single Drawer Dummy",
            "Wood": _dims_2(draw_s_h, draw_s_d, 2*r_sing_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_s_h, draw_s_d, 2*r_sing_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(4*r_sing_draw*draw_s_h + 4*r_sing_draw*draw_s_d, 1),
        })

    if r_doub_draw > 0:
        draw_s_h = drawer_height - 2*WOOD_IN
        draw_s_d = D - B - 3*WOOD
        draw_f_h = drawer_height - 2*WOOD
        draw_f_w = (L - 4*WOOD)/2
        draw_b_h = drawer_height - 2*WOOD_IN
        draw_b_w = (L - 4*WOOD)/2
        draw_bo_w = (L -  3*WOOD)/2
        draw_bo_d = D - B - 4*WOOD
        draw_fa_h = drawer_height - WOOD
        draw_fa_w = (L - WOOD_IN)/2

        rows.append({
            "Cut piece name": "Right Double Drawer Side Panel",
            "Wood": _dims_2(draw_s_h, draw_s_d, 2*r_doub_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_s_h, draw_s_d, 2*r_doub_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(4*r_doub_draw*draw_s_h + 4*r_doub_draw*draw_s_d, 1),
        })
        rows.append({
            "Cut piece name": "Right Double Drawer Front Panel",
            "Wood": _dims_2(draw_f_h, draw_f_w, r_doub_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_f_h, draw_f_w, r_doub_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(2*r_doub_draw*draw_f_h + 2*r_doub_draw*draw_f_w, 1),
        })
        rows.append({
            "Cut piece name": "Right Double Drawer Back Panel",
            "Wood": _dims_2(draw_b_h, draw_b_w, r_doub_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_b_h, draw_b_w, r_doub_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(2*r_doub_draw*draw_b_h + 2*r_doub_draw*draw_b_w, 1),
        })
        rows.append({
            "Cut piece name": f"Right Double Drawer Bottom ({int(B)}mm)",
            "Wood": _dims_2(draw_bo_w, draw_bo_d, r_doub_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_bo_w, draw_bo_d, r_doub_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": 0.0,
        })
        rows.append({
            "Cut piece name": "Right Double Drawer Fascia",
            "Wood": _dims_2(draw_fa_h, draw_fa_w, r_doub_draw),
            "Colour laminate": _dims_2(draw_fa_h, draw_fa_w, r_doub_draw),
            "White laminate": _dims_2(draw_fa_h, draw_fa_w, r_doub_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(2*r_doub_draw*draw_fa_h + 2*r_doub_draw*draw_fa_w, 1),
        })
        rows.append({
            "Cut piece name": "Right Double Drawer Dummy",
            "Wood": _dims_2(draw_s_h, draw_s_d, 2*r_doub_draw),
            "Colour laminate": "",
            "White laminate": _dims_2(draw_s_h, draw_s_d, 2*r_doub_draw),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(4*r_doub_draw*draw_s_h + 4*r_doub_draw*draw_s_d, 1),
        })

    if ver_shelf_height > 0:
          rows.append({
            "Cut piece name": "All Vertical Shelfs complete piece",
            "Wood": _dims_2(ver_shelf_height, part_w, 1),
            "Colour laminate": "",
            "White laminate": _dims_2(ver_shelf_height, part_w, 2),
            "Colour edge bidding": 0.0,
            "White edge bidding": round(2*ver_shelf_height + 2*part_w, 1),
        })
          
    df = pd.DataFrame(rows, columns=[
        "Cut piece name",
        "Wood",
        "Colour laminate",
        "White laminate",
        "Colour edge bidding",
        "White edge bidding",
    ])
    return df

