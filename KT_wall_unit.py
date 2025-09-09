# wardrobe_2door_slide.py
import math
from typing import Dict, List, Tuple
import pandas as pd
import streamlit as st

DEFAULTS = {
    # construction
    "wood_thick": 18.0,       # carcass core (MR/HDHMR) thickness
    "inside_lam": 1,        # laminate on inner faces
    "outside_lam": 2.0,       # laminate on outer faces
    "back_thick": 6.0,        # back board
    "plinth": 100.0,          # skirting height
    "groove": 7.0,            # groove depth for back/shelves
    "side_outside": True,     # sides outside top/bottom
    "side_expo": False,       # side panel exposed (no laminate on one side)
    # storage
    "shelves": 1,
    "doors": 1,

}

# ---------------- UI (all vertical, one-by-one) ----------------
def form_type1(prefill: Dict=None, button_label: str="Add"):
    if prefill is None:
        prefill = {}

    st.subheader("Kitchen Wall Unit – Inputs")


    height = st.number_input("Height (mm)", 100.0, 4200.0,
                             value=float(prefill.get("height", 710.0)), step=1.0, key="s_height")
    
    length = st.number_input("Width (mm)", 100.0, 5000.0,
                             value=float(prefill.get("length", 1021.0)), step=1.0, key="s_len")
    
    depth  = st.number_input("Depth (mm)", 100.0, 800.0,
                             value=float(prefill.get("depth", 580.0)), step=1.0, key="s_depth")

    shelves = st.number_input("Horizontal Shelves (qty)", 0, 16,
                              value=int(prefill.get("shelves", DEFAULTS["shelves"])), step=1, key="s_shelves")

    # NEW: thicknesses split as core + inside/outside laminates
    wood_thick = st.number_input("Wood Thickness (mm)", 12.0, 25.0,
                                 value=float(prefill.get("wood_thick", DEFAULTS["wood_thick"])), step=0.5, key="s_core")
    inside_lam = st.number_input("Inside Laminate Thickness (mm)", 0.0, 2.0,
                                 value=float(prefill.get("inside_lam", DEFAULTS["inside_lam"])), step=0.1, key="s_inlam")
    outside_lam = st.number_input("Outside Laminate Thickness (mm)", 0.0, 2.0,
                                  value=float(prefill.get("outside_lam", DEFAULTS["outside_lam"])), step=0.1, key="s_outlam")

    plinth = st.number_input("Skirting / Plinth (mm)", 0.0, 200.0,
                             value=float(prefill.get("plinth", DEFAULTS["plinth"])), step=1.0, key="s_plinth")

    back_thick = st.number_input("Back Thickness (mm)", 3.0, 9.0,
                                 value=float(prefill.get("back_thick", DEFAULTS["back_thick"])), step=0.5, key="s_bt")

    groove = st.number_input("Groove Allowance (mm)", 0.0, 10.0,
                             value=float(prefill.get("groove", DEFAULTS["groove"])), step=0.5, key="s_groove")

    submitted = st.form_submit_button(button_label)

    data = dict(
        length=length, height=height, depth=depth,
        wood_thick=wood_thick, inside_lam=inside_lam, outside_lam=outside_lam,
        back_thick=back_thick, groove=groove,plinth=plinth,shelves=shelves
    )
    return submitted, data

# --------------- helpers ---------------
def _fmt(name: str, qty: int, h: float, w: float, notes: str="") -> str:
    h = round(h, 1); w = round(w, 1)
    return f"{name}: {qty} pcs — {h} × {w} mm" + (f" — {notes}" if notes else "")

def _row(name, qty, h, w, notes=""):
    return dict(item=name, qty=int(qty), height_mm=round(h, 1), width_mm=round(w, 1), notes=notes)

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
    shelves = int(d["shelves"])

   
    WOOD_IN = WOOD + IN  #Wood + Inside laminate
    WOOD_OUT = WOOD + OUT  #Wood + Inside laminate
    WOOD_IN_OUT = WOOD + IN + OUT  #Wood + both laminates

    out: List[str] = []

    # --- carcass ---
    side_h = H 
    side_w = D - OUT
    out.append(_fmt("Left Panel", 1, side_h, side_w, f"{groove}mm - groove to back;"))
    out.append(_fmt("Right Panel", 1, side_h, side_w, f"{groove}mm - groove to back;"))

    # Top/Bottom length is between **inside faces of sides**
    tb_len = (L - 2*WOOD_OUT)
    tb_w  = D - OUT
    out.append(_fmt("Top Panel", 1, tb_len, tb_w, f"{WOOD}mm core; groove to back"))
    out.append(_fmt("Bottom Panel", 1, tb_len, tb_w, f"{WOOD}mm core; groove to back"))

    # Back panel(s): sit in grooves; height reduced by grooves on top/bottom
    back_h = H - (2*(WOOD_IN - groove))
    back_l = (L - WOOD_OUT)
    out.append(_fmt("Back Panel", 1, back_h, back_l, f"{WOOD}mm core;"))

    if shelves > 0:
        # Fixed shelf across carcass (between inside faces / includes partition allowance)
        shelf_len = (L - 2*WOOD_OUT)
        shelf_w   = D - B
        out.append(_fmt("Horizontal Shelf", shelves, shelf_len, shelf_w, f"{WOOD}mm core"))

    # Fixed shelf across carcass (between inside faces / includes partition allowance)
    door_h = H -2*OUT
    door_w = L/2 - 2*OUT
    out.append(_fmt("Doors", 2, door_h, door_w, f"{WOOD}mm core"))

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
    shelves = int(d["shelves"])

   
    WOOD_IN = WOOD + IN  #Wood + Inside laminate
    WOOD_OUT = WOOD + OUT  #Wood + Inside laminate
    WOOD_IN_OUT = WOOD + IN + OUT  #Wood + both laminates

    rows = []

    # --- carcass ---
    side_h = H 
    side_w = D - OUT
    rows.append(_row("Left Panel", 1, side_h, side_w, f"{groove}mm - groove to back;"))
    rows.append(_row("Right Panel", 1, side_h, side_w, f"{groove}mm - groove to back;"))

    # Top/Bottom length is between **inside faces of sides**
    tb_len = (L - 2*WOOD_OUT)
    tb_w  = D - OUT
    rows.append(_row("Top Panel", 1, tb_len, tb_w, f"{WOOD}mm core; groove to back"))
    rows.append(_row("Bottom Panel", 1, tb_len, tb_w, f"{WOOD}mm core; groove to back"))

    # Back panel(s): sit in grooves; height reduced by grooves on top/bottom
    back_h = H - (2*(WOOD_IN - groove))
    back_l = (L - WOOD_OUT)
    rows.append(_row("Back Panel", 1, back_h, back_l, f"{WOOD}mm core;"))

    if shelves > 0:
        # Fixed shelf across carcass (between inside faces / includes partition allowance)
        shelf_len = (L - 2*WOOD_OUT)
        shelf_w   = D - B
        rows.append(_row("Horizontal Shelf", shelves, shelf_len, shelf_w, f"{WOOD}mm core"))

    # Fixed shelf across carcass (between inside faces / includes partition allowance)
    door_h = H -2*OUT
    door_w = L/2 - 2*OUT
    rows.append(_row("Doors", 2, door_h, door_w, f"{WOOD}mm core"))
    
    return pd.DataFrame(rows)
