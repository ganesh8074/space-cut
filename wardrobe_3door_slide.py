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

    st.subheader("2-Door Wardrobe – Inputs")


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
    drawers = int(d["drawers"])
    drawer_height = float(d["draw_height"])
    overlap = float(d.get("overlap", 60.0))

    rows = []

    WOOD_IN = WOOD + IN
    WOOD_OUT = WOOD + OUT
    WOOD_IN_OUT = WOOD + IN + OUT

    # Sides
    side_h = H/2
    side_w = D - OUT
    for label in ["Left Panel", "Right Panel"]:
        rows.append({
            "Cut piece name": label,
            "Wood": _dims(side_h, side_w),
            "Colour laminate": _dims(side_h, side_w),
            "White laminate": _dims(side_h, side_w),
            "Colour edge bidding": round(H + D, 1),
            "White edge bidding": round(D, 1),
        })

    # Center partitions (2 for 3 bays)
    part_h = H - P - WOOD_IN_OUT
    part_w = D - B - 3*WOOD
    for i in range(2):
        rows.append({
            "Cut piece name": f"Center Partition {i+1}",
            "Wood": _dims(part_h, part_w),
            "Colour laminate": _dims(part_h, part_w),
            "White laminate": _dims(part_h, part_w),
            "Colour edge bidding": round(2*part_h + 2*part_w, 1),
            "White edge bidding": 0.0,
        })

    # Top/Bottom
    tb_len = (L - 2*WOOD_OUT) if side_outside else L
    tb_w   = D - OUT
    for label in ["Top Panel", "Bottom Panel"]:
        rows.append({
            "Cut piece name": label,
            "Wood": _dims(tb_len, tb_w),
            "Colour laminate": _dims(tb_len, tb_w),
            "White laminate": _dims(tb_len, tb_w),
            "Colour edge bidding": round(tb_len, 1),
            "White edge bidding": round(tb_w, 1),
        })

    # Back panels (split into 3 for 3 bays)
    back_h = H - P - (2*(WOOD_IN - groove))
    back_l = (L - 2*WOOD_OUT - WOOD + 4*groove)/3
    for i in range(3):
        rows.append({
            "Cut piece name": f"Back Panel {i+1} ({int(B)}mm)",
            "Wood": _dims(back_h, back_l),
            "Colour laminate": "",
            "White laminate": _dims(back_h, back_l),
            "Colour edge bidding": 0.0,
            "White edge bidding": 0.0,
        })

    # Doors (3 sliding leaves)
    door_h = H - P - WOOD_IN_OUT
    door_w = (L + 2*overlap) / 3
    for i in range(3):
        rows.append({
            "Cut piece name": f"Door {i+1}",
            "Wood": _dims(door_h, door_w),
            "Colour laminate": _dims(door_h, door_w),
            "White laminate": _dims(door_h, door_w),
            "Colour edge bidding": round(2*door_h + 2*door_w, 1),
            "White edge bidding": 0.0,
        })

    # Bottom skirting
    rows.append({
        "Cut piece name": "Bottom SKT",
        "Wood": _dims(P, L),
        "Colour laminate": _dims(P, L),
        "White laminate": "",
        "Colour edge bidding": round(2*P + L, 1),
        "White edge bidding": round(L, 1),
    })

    # Shelves (3 bays)
    shelf_len = (L - 2*WOOD_OUT - WOOD) / 3
    shelf_w   = D - B - 3*WOOD
    if shelves > 0:
        for i in range(3):
            rows.append({
                "Cut piece name": f"Horizontal Shelf Bay {i+1}",
                "Wood": _dims(shelf_len, shelf_w),
                "Colour laminate": _dims(shelf_len, shelf_w),
                "White laminate": _dims(shelf_len, shelf_w),
                "Colour edge bidding": 0.0,
                "White edge bidding": round(2*shelf_len + 2*shelf_w, 1),
            })

    # Drawers (3 bays)
    if drawers > 0:
        for i in range(3):
            draw_s_h = drawer_height - 2*WOOD_IN
            draw_s_d = shelf_w
            draw_f_h = drawer_height - 2*WOOD
            draw_f_w = shelf_len
            draw_b_h = drawer_height - 2*WOOD_IN
            draw_b_w = shelf_len
            draw_bo_w = shelf_len
            draw_bo_d = shelf_w
            draw_fa_h = drawer_height - WOOD
            draw_fa_w = shelf_len

            rows.append({
                "Cut piece name": f"Drawer Side Panel Bay {i+1}",
                "Wood": _dims(draw_s_h, draw_s_d),
                "Colour laminate": "",
                "White laminate": _dims(draw_s_h, draw_s_d),
                "Colour edge bidding": 0.0,
                "White edge bidding": 0.0,
            })
            rows.append({
                "Cut piece name": f"Drawer Front Panel Bay {i+1}",
                "Wood": _dims(draw_f_h, draw_f_w),
                "Colour laminate": "",
                "White laminate": _dims(draw_f_h, draw_f_w),
                "Colour edge bidding": 0.0,
                "White edge bidding": 0.0,
            })
            rows.append({
                "Cut piece name": f"Drawer Back Panel Bay {i+1}",
                "Wood": _dims(draw_b_h, draw_b_w),
                "Colour laminate": "",
                "White laminate": _dims(draw_b_h, draw_b_w),
                "Colour edge bidding": 0.0,
                "White edge bidding": 0.0,
            })
            rows.append({
                "Cut piece name": f"Drawer Bottom Bay {i+1} ({int(B)}mm)",
                "Wood": _dims(draw_bo_w, draw_bo_d),
                "Colour laminate": "",
                "White laminate": _dims(draw_bo_w, draw_bo_d),
                "Colour edge bidding": 0.0,
                "White edge bidding": 0.0,
            })
            rows.append({
                "Cut piece name": f"Drawer Fascia Bay {i+1}",
                "Wood": _dims(draw_fa_h, draw_fa_w),
                "Colour laminate": _dims(draw_fa_h, draw_fa_w),
                "White laminate": _dims(draw_fa_h, draw_fa_w),
                "Colour edge bidding": 0.0,
                "White edge bidding": 0.0,
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
