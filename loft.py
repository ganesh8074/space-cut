import math
from typing import Dict, List, Tuple
import pandas as pd
import streamlit as st

DEFAULTS = {
    # construction
    "wood_thick": 18.0,       # carcass core (MR/HDHMR) thickness
    "inside_lam": 0.8,        # laminate on inner faces
    "outside_lam": 1.0,       # laminate on outer faces
    "side_outside": True,  
    "doors":4   # sides outside top/bottom

}

# ---------------- UI (all vertical, one-by-one) ----------------
def form_type1(prefill: Dict=None, button_label: str="Add"):
    if prefill is None:
        prefill = {}

    st.subheader("Wardrobe LOFT – Inputs")


    height = st.number_input("Height (mm)", 100.0, 4200.0,
                             value=float(prefill.get("height", 600.0)), step=1.0, key="s_height")
    
    length = st.number_input("Width (mm)", 100.0, 5000.0,
                             value=float(prefill.get("length", 2350.0)), step=1.0, key="s_len")
    
    depth  = st.number_input("Depth (mm)", 100.0, 800.0,
                             value=float(prefill.get("depth", 600.0)), step=1.0, key="s_depth")
    
    filler  = st.number_input("Filler (mm)", 10.0, 1000.0,
                             value=float(prefill.get("filler", 40.0)), step=1.0, key="s_filler")

    doors = st.number_input("Doors (qty)", 0, 8,
                              value=int(prefill.get("doors", DEFAULTS["doors"])), step=1, key="s_drawers")

    # NEW: thicknesses split as core + inside/outside laminates
    wood_thick = st.number_input("Wood Thickness (mm)", 12.0, 25.0,
                                 value=float(prefill.get("wood_thick", DEFAULTS["wood_thick"])), step=0.5, key="s_core")
    inside_lam = st.number_input("Inside Laminate Thickness (mm)", 0.0, 2.0,
                                 value=float(prefill.get("inside_lam", DEFAULTS["inside_lam"])), step=0.1, key="s_inlam")
    outside_lam = st.number_input("Outside Laminate Thickness (mm)", 0.0, 2.0,
                                  value=float(prefill.get("outside_lam", DEFAULTS["outside_lam"])), step=0.1, key="s_outlam")

    side_outside = st.selectbox("Assembly preference",
                                ["Side panels outside", "Top/Bottom outside"],
                                index=0 if prefill.get("side_outside", DEFAULTS["side_outside"]) else 1,
                                key="s_side_out").startswith("Side")

    # Laminate color inputs
    st.subheader("Laminate Colors")
    left_panel_color = st.text_input("Left Side Panel Color", value=prefill.get("left_panel_color", "18 mm MR PLY FB BSL"), key="s_left_color")
    right_panel_color = st.text_input("Right Side Panel Color", value=prefill.get("right_panel_color", "18 mm MR PLY FB BSL"), key="s_right_color")
    top_panel_color = st.text_input("Top Panel Color", value=prefill.get("top_panel_color", "18 mm MR PLY 3272 SF +FB OSL"), key="s_top_color")
    inner_color = st.text_input("Inner Color (bottom, back, etc.)", value=prefill.get("inner_color", "18 mm MR PLY FB BSL"), key="s_inner_color")
    door_color = st.text_input("Shutter Color", value=prefill.get("door_color", "18 mm MR PLY 3272 SF +FB OSL"), key="s_door_color")
    drawer_facia_color = st.text_input("Facia Color", value=prefill.get("drawer_facia_color", "18 mm MR PLY 188- ZMT +FB OSL"), key="s_drawer_facia_color")
    skt_color = st.text_input("SKT Color", value=prefill.get("skt_color", "18 mm MR PLY 3272 SF +FB OSL"), key="s_skt_color")

    submitted = st.form_submit_button(button_label)

    data = dict(
        length=length, height=height, depth=depth,
        wood_thick=wood_thick, inside_lam=inside_lam, outside_lam=outside_lam,
        filler=filler,
        side_outside=side_outside,doors=doors,
        left_panel_color=left_panel_color, right_panel_color=right_panel_color,
        top_panel_color=top_panel_color, inner_color=inner_color, door_color=door_color,
        drawer_facia_color=drawer_facia_color, skt_color=skt_color,
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
    side_outside = bool(d["side_outside"])
    filler_w = int(d["filler"])
    doors = int(d["doors"])

    WOOD_IN = WOOD + IN  #Wood + Inside laminate
    WOOD_OUT = WOOD + OUT  #Wood + Inside laminate
    WOOD_IN_OUT = WOOD + IN + OUT  #Wood + both laminates

    out: List[str] = []

    if doors > 2 : center_panel = 1

    out.append(_fmt(f"Loft Doors", doors, H, L/4, f"{WOOD}mm core"))
    out.append(_fmt(f"Center Panel", center_panel, H , D, f"{WOOD}mm core"))
    out.append(_fmt(f"Expo Panel Side", 1, H, D, f"{WOOD}mm core"))
    out.append(_fmt(f"Dummy", 1, H, filler_w, f"{WOOD}mm core"))
    out.append(_fmt(f"Dummy", 1, L + 2*WOOD_IN_OUT, filler_w, f"{WOOD}mm core"))
    out.append(_fmt(f"Ripper", 1, L + 2*WOOD_IN_OUT, 98, f"{WOOD}mm core"))

    return out


def get_cutlist_df(d: Dict) -> pd.DataFrame:
    L = float(d["length"])
    H = float(d["height"])
    D = float(d["depth"])
    WOOD = float(d["wood_thick"])
    IN = float(d["inside_lam"])
    OUT = float(d["outside_lam"])
    side_outside = bool(d["side_outside"])
    filler_w = int(d["filler"])
    doors = int(d["doors"])
    # Get laminate colors from input
    left_panel_color = d.get("left_panel_color", "")
    right_panel_color = d.get("right_panel_color", "")
    top_panel_color = d.get("top_panel_color", "")
    inner_color = d.get("inner_color", "")
    door_color = d.get("door_color", "")
    drawer_facia_color = d.get("drawer_facia_color", "")
    skt_color = d.get("skt_color", "")
    
    if doors > 2:
        center_panel = 1
    else:
        center_panel = 0

    WOOD_IN = WOOD + IN  # Wood + Inside laminate
    WOOD_OUT = WOOD + OUT  # Wood + Outside laminate
    WOOD_IN_OUT = WOOD + IN + OUT  # Wood + both laminates

    def dims(h, w):
        return f"{round(h,1)} × {round(w,1)}"

    def dims_2(h, w, qty):
        return f"{round(h,1)} × {round(w,1)} = {qty} qty"

    rows = []

    # Loft Doors
    rows.append({
        "Cut piece name": "Loft Doors",
        "Wood": dims_2(H, L/4, doors),
        "Colour laminate": dims_2(H, L/4, doors),
        "Laminate Color": door_color,
            "Short side 1": dims_2(H, L/4, doors),
        "Short side 2": round(2*H + 2*(L/4), 1),
        "Long side 1": 0.0,
    })
    # Center Panel
    if center_panel:
        rows.append({
            "Cut piece name": "Center Panel",
            "Wood": dims(H, D),
            "Colour laminate": dims(H, D),
            "Laminate Color": door_color,
            "Short side 1": dims(H, D),
            "Short side 2": round(2*H + 2*D, 1),
            "Long side 1": 0.0,
        })
    # Expo Panel Side
    rows.append({
        "Cut piece name": "Expo Panel Side",
        "Wood": dims(H, D),
        "Colour laminate": dims(H, D),
        "Laminate Color": inner_color,
        "Short side 1": dims(H, D),
        "Short side 2": round(2*H + 2*D, 1),
        "Long side 1": 0.0,
    })
    # Dummy (vertical)
    rows.append({
        "Cut piece name": "Dummy (vertical)",
        "Wood": dims(H, filler_w),
        "Colour laminate": dims(H, filler_w),
        "Laminate Color": door_color,
            "Short side 1": dims(H, filler_w),
        "Short side 2": round(2*H + 2*filler_w, 1),
        "Long side 1": 0.0,
    })
    # Dummy (horizontal)
    rows.append({
        "Cut piece name": "Dummy (horizontal)",
        "Wood": dims(L + 2*WOOD_IN_OUT, filler_w),
        "Colour laminate": dims(L + 2*WOOD_IN_OUT, filler_w),
        "Laminate Color": door_color,
            "Short side 1": dims(L + 2*WOOD_IN_OUT, filler_w),
        "Short side 2": round(2*(L + 2*WOOD_IN_OUT) + 2*filler_w, 1),
        "Long side 1": 0.0,
    })
    # Ripper
    rows.append({
        "Cut piece name": "Ripper",
        "Wood": dims(L + 2*WOOD_IN_OUT, 98),
        "Colour laminate": dims(L + 2*WOOD_IN_OUT, 98),
        "Laminate Color": door_color,
            "Short side 1": dims(L + 2*WOOD_IN_OUT, 98),
        "Short side 2": 0.0,
        "Long side 1": round(2*(L + 2*WOOD_IN_OUT) + 2*98, 1),
    })

    df = pd.DataFrame(rows, columns=[
        "Cut piece name",
        "Wood",
        "Colour laminate",
        "Laminate Color",
        "Short side 1",
        "Short side 2",
        "Long side 1",
        "Long side 2",
        "Groove",
    ])
    return df
