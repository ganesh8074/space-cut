import math
from typing import Dict, List, Tuple
import pandas as pd
import streamlit as st

DEFAULTS = {
    # construction
    "wood_thick": 18.0,       # carcass core (MR/HDHMR) thickness
    "inside_lam": 1.0,        # laminate on inner faces
    "outside_lam": 2.0,       # laminate on outer faces
    "back_thick": 6.0,        # back board
    "groove": 7.0,            # groove depth for back/shelves
    "side_outside": True,     # sides outside top/bottom
    
    # kitchen defaults
    "base_height": 710.0,
    "base_depth": 580.0,
    "wall_height": 300.0,
    "wall_depth": 325.0,
    "loft_height": 540.0,
    "loft_depth": 325.0,
}

def _dims(h, w):
    # compact dimension string (no qty, mm implied)
    return f"{round(h,1)} × {round(w,1)}"

def _dims_2(h, w, qty):
    # compact dimension string with qty (mm implied)
    return f"{round(h,1)} × {round(w,1)} = {qty} qty"

# ---------------- UI (all vertical, one-by-one) ----------------
def form_type1(prefill: Dict=None, button_label: str="Add"):
    if prefill is None:
        prefill = {}
    
    st.subheader("Kitchen – Inputs")
    
    # Base Unit Dimensions
    st.markdown("### Base Unit Dimensions")
    base_height = st.number_input("Base Unit Height (mm)", 400.0, 1000.0,
                                   value=float(prefill.get("base_height", DEFAULTS["base_height"])), step=1.0, key="k_base_h")
    base_depth = st.number_input("Base Unit Depth (mm)", 400.0, 800.0,
                                  value=float(prefill.get("base_depth", DEFAULTS["base_depth"])), step=1.0, key="k_base_d")
    
    # Base Unit Modules
    st.markdown("### Base Unit Modules")
    
    # BPO (Bottle Pull Out)
    has_bpo = st.checkbox("BPO (Bottle Pull Out) Needed?", value=bool(prefill.get("has_bpo", False)), key="k_has_bpo")
    bpo_width = 0.0
    if has_bpo:
        bpo_width = st.number_input("BPO Width (mm)", 200.0, 2000.0,
                                     value=float(prefill.get("bpo_width", 1025.0)), step=1.0, key="k_bpo_w")
    
    # Tandem
    has_tandem = st.checkbox("Tandem Needed?", value=bool(prefill.get("has_tandem", False)), key="k_has_tandem")
    tandem_type = None
    tandem_width = 0.0
    tandem_count = 0
    if has_tandem:
        tandem_type = st.selectbox("Tandem Type", ["2-door", "3-door"],
                                   index=0 if prefill.get("tandem_type", "2-door") == "2-door" else 1,
                                   key="k_tandem_type")
        tandem_width = st.number_input("Tandem Width (mm)", 200.0, 2000.0,
                                       value=float(prefill.get("tandem_width", 600.0)), step=1.0, key="k_tandem_w")
        tandem_count = st.number_input("No of Tandems", 1, 10,
                                       value=int(prefill.get("tandem_count", 1)), step=1, key="k_tandem_count")
    
    # Sink Unit
    has_sink_unit = st.checkbox("Sink Unit Needed?", value=bool(prefill.get("has_sink_unit", False)), key="k_has_sink")
    sink_width = 0.0
    sink_doors = 0
    if has_sink_unit:
        sink_width = st.number_input("Sink Unit Width (mm)", 200.0, 2000.0,
                                     value=float(prefill.get("sink_width", 670.0)), step=1.0, key="k_sink_w")
        sink_doors = st.number_input("Sink Unit No of Doors", 1, 4,
                                     value=int(prefill.get("sink_doors", 2)), step=1, key="k_sink_doors")
    
    # Blind Corner Unit
    has_blind_corner = st.checkbox("Blind Corner Unit Needed?", value=bool(prefill.get("has_blind_corner", False)), key="k_has_blind")
    blind_corner_width = 0.0
    blind_corner_shelf = False
    if has_blind_corner:
        blind_corner_width = st.number_input("Blind Corner Unit Width (mm)", 200.0, 2000.0,
                                             value=float(prefill.get("blind_corner_width", 1570.0)), step=1.0, key="k_blind_w")
        blind_corner_shelf = st.checkbox("Fixed Shelf in Blind Corner?", 
                                        value=bool(prefill.get("blind_corner_shelf", True)), key="k_blind_shelf")
    
    # Regular Base Cabinets
    st.markdown("### Regular Base Cabinets")
    base_cabinets = st.number_input("No of Regular Base Cabinets", 0, 20,
                                     value=int(prefill.get("base_cabinets", 0)), step=1, key="k_base_cab")
    
    base_cabinet_details = []
    if base_cabinets > 0:
        for i in range(base_cabinets):
            st.markdown(f"**Cabinet {i+1}**")
            cab_width = st.number_input(f"Cabinet {i+1} Width (mm)", 200.0, 2000.0,
                                        value=float(prefill.get(f"base_cab_{i}_width", 600.0)), step=1.0, key=f"k_base_cab_{i}_w")
            cab_doors = st.number_input(f"Cabinet {i+1} No of Doors", 1, 4,
                                        value=int(prefill.get(f"base_cab_{i}_doors", 1)), step=1, key=f"k_base_cab_{i}_doors")
            cab_shelves = st.number_input(f"Cabinet {i+1} No of Shelves", 0, 10,
                                          value=int(prefill.get(f"base_cab_{i}_shelves", 0)), step=1, key=f"k_base_cab_{i}_shelves")
            base_cabinet_details.append({"width": cab_width, "doors": cab_doors, "shelves": cab_shelves})
    
    # Wall Unit Dimensions
    st.markdown("### Wall Unit Dimensions")
    wall_height = st.number_input("Wall Unit Height (mm)", 200.0, 1000.0,
                                  value=float(prefill.get("wall_height", DEFAULTS["wall_height"])), step=1.0, key="k_wall_h")
    wall_depth = st.number_input("Wall Unit Depth (mm)", 250.0, 400.0,
                                  value=float(prefill.get("wall_depth", DEFAULTS["wall_depth"])), step=1.0, key="k_wall_d")
    
    # Wall Units
    st.markdown("### Wall Units")
    wall_unit_1 = st.checkbox("Wall Unit-1 (Standard)", value=bool(prefill.get("wall_unit_1", False)), key="k_wall_1")
    wall_unit_1_width = 0.0
    if wall_unit_1:
        wall_unit_1_width = st.number_input("Wall Unit-1 Width (mm)", 200.0, 2000.0,
                                            value=float(prefill.get("wall_unit_1_width", 1025.0)), step=1.0, key="k_wall_1_w")
    
    wall_unit_2_corner = st.checkbox("Wall Unit-2-L Corner", value=bool(prefill.get("wall_unit_2_corner", False)), key="k_wall_2")
    wall_unit_2_width = 0.0
    if wall_unit_2_corner:
        wall_unit_2_width = st.number_input("Wall Unit-2-L Corner Width (mm)", 200.0, 2000.0,
                                            value=float(prefill.get("wall_unit_2_width", 630.0)), step=1.0, key="k_wall_2_w")
    
    wall_unit_3_open = st.checkbox("Wall Unit-3-Open Unit", value=bool(prefill.get("wall_unit_3_open", False)), key="k_wall_3")
    wall_unit_3_width = 0.0
    if wall_unit_3_open:
        wall_unit_3_width = st.number_input("Wall Unit-3-Open Width (mm)", 200.0, 2000.0,
                                           value=float(prefill.get("wall_unit_3_width", 630.0)), step=1.0, key="k_wall_3_w")
    
    wall_unit_4_profile = st.checkbox("Wall Unit-4 Profile SS Unit", value=bool(prefill.get("wall_unit_4_profile", False)), key="k_wall_4")
    wall_unit_4_width = 0.0
    wall_unit_4_doors = 0
    if wall_unit_4_profile:
        wall_unit_4_width = st.number_input("Wall Unit-4 Profile Width (mm)", 200.0, 2000.0,
                                           value=float(prefill.get("wall_unit_4_width", 670.0)), step=1.0, key="k_wall_4_w")
        wall_unit_4_doors = st.number_input("Wall Unit-4 No of Doors", 1, 4,
                                           value=int(prefill.get("wall_unit_4_doors", 2)), step=1, key="k_wall_4_doors")
    
    # Loft Unit Dimensions
    st.markdown("### Loft Unit Dimensions")
    loft_height = st.number_input("Loft Unit Height (mm)", 200.0, 600.0,
                                   value=float(prefill.get("loft_height", DEFAULTS["loft_height"])), step=1.0, key="k_loft_h")
    loft_depth = st.number_input("Loft Unit Depth (mm)", 300.0, 500.0,
                                 value=float(prefill.get("loft_depth", DEFAULTS["loft_depth"])), step=1.0, key="k_loft_d")
    
    # Loft Units
    st.markdown("### Loft Units")
    loft_shutters = st.number_input("No of Loft Shutters", 0, 20,
                                    value=int(prefill.get("loft_shutters", 0)), step=1, key="k_loft_shutters")
    loft_shutter_width = 0.0
    if loft_shutters > 0:
        loft_shutter_width = st.number_input("Loft Shutter Width (mm)", 200.0, 2000.0,
                                             value=float(prefill.get("loft_shutter_width", 445.0)), step=1.0, key="k_loft_shutter_w")
    
    loft_bottom_expo_count = st.number_input("No of Loft Bottom Expo", 0, 10,
                                            value=int(prefill.get("loft_bottom_expo_count", 0)), step=1, key="k_loft_expo")
    loft_bottom_expo_widths = []
    if loft_bottom_expo_count > 0:
        for i in range(loft_bottom_expo_count):
            expo_w = st.number_input(f"Loft Bottom Expo {i+1} Width (mm)", 200.0, 3000.0,
                                     value=float(prefill.get(f"loft_expo_{i}_width", 2200.0)), step=1.0, key=f"k_loft_expo_{i}_w")
            loft_bottom_expo_widths.append(expo_w)
    
    # Construction details
    st.markdown("### Construction Details")
    wood_thick = st.number_input("Wood Thickness (mm)", 12.0, 25.0,
                                 value=float(prefill.get("wood_thick", DEFAULTS["wood_thick"])), step=0.5, key="k_wood")
    inside_lam = st.number_input("Inside Laminate Thickness (mm)", 0.0, 2.0,
                                 value=float(prefill.get("inside_lam", DEFAULTS["inside_lam"])), step=0.1, key="k_inlam")
    outside_lam = st.number_input("Outside Laminate Thickness (mm)", 0.0, 2.0,
                                  value=float(prefill.get("outside_lam", DEFAULTS["outside_lam"])), step=0.1, key="k_outlam")
    back_thick = st.number_input("Back Thickness (mm)", 3.0, 9.0,
                                 value=float(prefill.get("back_thick", DEFAULTS["back_thick"])), step=0.5, key="k_back")
    groove = st.number_input("Groove Allowance (mm)", 0.0, 10.0,
                             value=float(prefill.get("groove", DEFAULTS["groove"])), step=0.5, key="k_groove")
    
    # Color codes
    st.markdown("### Color Codes")
    base_color = st.text_input("Base Unit Color Code", 
                               value=prefill.get("base_color", "18 mm BWP PLY FB BSL"), 
                               key="k_base_color")
    wall_color = st.text_input("Wall Unit Color Code", 
                               value=prefill.get("wall_color", "18 mm HDHMR 255-LU +FB OSL"), 
                               key="k_wall_color")
    loft_color = st.text_input("Loft Unit Color Code", 
                               value=prefill.get("loft_color", "18 mm HDHMR 255-LU +FB OSL"), 
                               key="k_loft_color")
    facia_color = st.text_input("Facia Color Code",
                                value=prefill.get("facia_color", "18 mm HDHMR 107-LU +FB OSL"),
                                key="k_facia_color")
    shutter_color = st.text_input("Shutter Color Code",
                                  value=prefill.get("shutter_color", "18 mm HDHMR 107-LU +FB OSL"),
                                  key="k_shutter_color")
    
    submitted = st.form_submit_button(button_label)
    
    # Prepare data dict
    data = dict(
        base_height=base_height, base_depth=base_depth,
        wall_height=wall_height, wall_depth=wall_depth,
        loft_height=loft_height, loft_depth=loft_depth,
        wood_thick=wood_thick, inside_lam=inside_lam, outside_lam=outside_lam,
        back_thick=back_thick, groove=groove,
        has_bpo=has_bpo, bpo_width=bpo_width,
        has_tandem=has_tandem, tandem_type=tandem_type, tandem_width=tandem_width, tandem_count=tandem_count,
        has_sink_unit=has_sink_unit, sink_width=sink_width, sink_doors=sink_doors,
        has_blind_corner=has_blind_corner, blind_corner_width=blind_corner_width, blind_corner_shelf=blind_corner_shelf,
        base_cabinets=base_cabinets,
        wall_unit_1=wall_unit_1, wall_unit_1_width=wall_unit_1_width,
        wall_unit_2_corner=wall_unit_2_corner, wall_unit_2_width=wall_unit_2_width,
        wall_unit_3_open=wall_unit_3_open, wall_unit_3_width=wall_unit_3_width,
        wall_unit_4_profile=wall_unit_4_profile, wall_unit_4_width=wall_unit_4_width, wall_unit_4_doors=wall_unit_4_doors,
        loft_shutters=loft_shutters, loft_shutter_width=loft_shutter_width,
        loft_bottom_expo_count=loft_bottom_expo_count,
        base_color=base_color, wall_color=wall_color, loft_color=loft_color,
        facia_color=facia_color, shutter_color=shutter_color,
    )
    
    # Add cabinet details
    for i, cab in enumerate(base_cabinet_details):
        data[f"base_cab_{i}_width"] = cab["width"]
        data[f"base_cab_{i}_doors"] = cab["doors"]
        data[f"base_cab_{i}_shelves"] = cab["shelves"]
    
    # Add loft expo widths
    for i, expo_w in enumerate(loft_bottom_expo_widths):
        data[f"loft_expo_{i}_width"] = expo_w
    
    return submitted, data

def calc_type1(d: Dict):
    """
    Keep for backward compatibility, but don't emit bullet strings.
    The main app will render the DataFrame returned by get_cutlist_df().
    """
    return []  # we want the table, not bullets

def get_cutlist_df(d: Dict) -> pd.DataFrame:
    # Extract dimensions
    base_h = float(d["base_height"])
    base_d = float(d["base_depth"])
    wall_h = float(d["wall_height"])
    wall_d = float(d["wall_depth"])
    loft_h = float(d["loft_height"])
    loft_d = float(d["loft_depth"])
    
    # Construction details
    WOOD = float(d["wood_thick"])
    IN = float(d["inside_lam"])
    OUT = float(d["outside_lam"])
    B = float(d["back_thick"])
    groove = float(d["groove"])
    
    # Colors
    base_color = d.get("base_color", "")
    wall_color = d.get("wall_color", "")
    loft_color = d.get("loft_color", "")
    facia_color = d.get("facia_color", "")
    shutter_color = d.get("shutter_color", "")
    
    WOOD_IN = WOOD + IN
    WOOD_OUT = WOOD + OUT
    WOOD_IN_OUT = WOOD + IN + OUT
    
    rows = []
    
    # ========== BPO & TANDEM SECTION ==========
    if d.get("has_bpo", False) or d.get("has_tandem", False):
        # Add heading row for BPO & Tandems section
        tandem_count = int(d.get("tandem_count", 0)) if d.get("has_tandem", False) else 0
        heading = "BPO" if d.get("has_bpo", False) and not d.get("has_tandem", False) else f"BPO & {tandem_count} Tandems" if d.get("has_bpo", False) else f"{tandem_count} Tandems"
        rows.append({
            "Cut piece name": heading,
            "Wood": "",
            "Colour laminate": "",
            "Laminate Color": "",
            "Short side 1": "", "Short side 2": "", "Long side 1": "", "Long side 2": "", "Groove": "",
        })
    
    # ========== BPO (BOTTLE PULL OUT) ==========
    if d.get("has_bpo", False):
        bpo_w = float(d.get("bpo_width", 1025.0))
        
        # Left side panel
        rows.append({
            "Cut piece name": "Left side panel",
            "Wood": _dims(base_h, base_d - OUT),
            "Colour laminate": _dims(base_h, base_d - OUT),
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Right side panel
        rows.append({
            "Cut piece name": "Right side panel",
            "Wood": _dims(base_h, base_d - OUT),
            "Colour laminate": _dims(base_h, base_d - OUT),
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Top Panel
        top_w = bpo_w - 2*WOOD_OUT
        rows.append({
            "Cut piece name": "Top Panel",
            "Wood": _dims(top_w, base_d - OUT),
            "Colour laminate": _dims(top_w, base_d - OUT),
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Bottom panel
        rows.append({
            "Cut piece name": "Bottom panel",
            "Wood": _dims(top_w, base_d - OUT),
            "Colour laminate": _dims(top_w, base_d - OUT),
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Back 6mm
        back_h_calc = base_h - 2*(WOOD_IN - groove)
        back_w_calc = bpo_w - WOOD_OUT
        rows.append({
            "Cut piece name": f"Back {int(B)}mm",
            "Wood": _dims(back_h_calc, back_w_calc),
            "Colour laminate": "",
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Vertical panel
        vert_h = base_h - WOOD_IN_OUT
        vert_w = base_d - B - 50
        rows.append({
            "Cut piece name": "Vertical panel",
            "Wood": _dims(vert_h, vert_w),
            "Colour laminate": "",
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
    
    # ========== TANDEM ==========
    if d.get("has_tandem", False):
        tandem_w = float(d.get("tandem_width", 600.0))
        tandem_count = int(d.get("tandem_count", 1))
        tandem_type = d.get("tandem_type", "2-door")
        
        # Tandem Bottom
        tandem_bottom_w = tandem_w - 2*WOOD_OUT
        tandem_bottom_d = base_d - B - 50
        rows.append({
            "Cut piece name": "Tandem Bottom",
            "Wood": _dims_2(tandem_bottom_w, tandem_bottom_d, tandem_count),
            "Colour laminate": "",
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Tandem Back (different sizes based on door count)
        tandem_back_h = base_h - 2*(WOOD_IN - groove)
        if tandem_type == "2-door":
            # Two sizes: 638x68 (2 pieces) and 638x145 (1 piece)
            rows.append({
                "Cut piece name": "Tandem Back",
                "Wood": _dims_2(tandem_back_h, 68, 2),
                "Colour laminate": "",
                "Laminate Color": base_color,
                "Short side 1": "",
                "Short side 2": "",
                "Long side 1": "",
                "Long side 2": "",
                "Groove": "",
            })
            rows.append({
                "Cut piece name": "Tandem Back",
                "Wood": _dims(tandem_back_h, 145),
                "Colour laminate": "",
                "Laminate Color": base_color,
                "Short side 1": "",
                "Short side 2": "",
                "Long side 1": "",
                "Long side 2": "",
                "Groove": "",
            })
        else:  # 3-door
            # Similar logic for 3-door configuration
            rows.append({
                "Cut piece name": "Tandem Back",
                "Wood": _dims_2(tandem_back_h, 68, 3),
                "Colour laminate": "",
                "Laminate Color": base_color,
                "Short side 1": "",
                "Short side 2": "",
                "Long side 1": "",
                "Long side 2": "",
                "Groove": "",
            })
        
        # Facia for tandems
        facia_h = base_h - WOOD_IN_OUT
        if tandem_type == "2-door":
            facia_w_1 = (tandem_w - WOOD_IN) / 2
            rows.append({
                "Cut piece name": "Facia",
                "Wood": _dims_2(facia_h, facia_w_1, 2),
                "Colour laminate": _dims_2(facia_h, facia_w_1, 2),
                "Laminate Color": facia_color,
                "Short side 1": "",
                "Short side 2": "",
                "Long side 1": "",
                "Long side 2": "",
                "Groove": "",
            })
            facia_w_2 = tandem_w - WOOD_IN - facia_w_1
            rows.append({
                "Cut piece name": "Facia",
                "Wood": _dims(facia_h, facia_w_2),
                "Colour laminate": _dims(facia_h, facia_w_2),
                "Laminate Color": facia_color,
                "Short side 1": "",
                "Short side 2": "",
                "Long side 1": "",
                "Long side 2": "",
                "Groove": "",
            })
        else:  # 3-door
            facia_w = (tandem_w - WOOD_IN) / 3
            rows.append({
                "Cut piece name": "Facia",
                "Wood": _dims_2(facia_h, facia_w, 3),
                "Colour laminate": _dims_2(facia_h, facia_w, 3),
                "Laminate Color": facia_color,
                "Short side 1": "",
                "Short side 2": "",
                "Long side 1": "",
                "Long side 2": "",
                "Groove": "",
            })
        
        # Shutter for tandem
        shutter_h = base_h - WOOD_IN_OUT
        shutter_w = tandem_w / (3 if tandem_type == "3-door" else 2)
        rows.append({
            "Cut piece name": "Shutter",
            "Wood": _dims(shutter_h, shutter_w),
            "Colour laminate": _dims(shutter_h, shutter_w),
            "Laminate Color": shutter_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Dummy
        rows.append({
            "Cut piece name": "Dummy",
            "Wood": _dims(base_h, 50),
            "Colour laminate": "",
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
    
    # ========== BLIND CORNER UNIT ==========
    if d.get("has_blind_corner", False):
        # Add heading row for Blind Corner Unit
        rows.append({
            "Cut piece name": "Blind corner unit",
            "Wood": "",
            "Colour laminate": "",
            "Laminate Color": "",
            "Short side 1": "", "Short side 2": "", "Long side 1": "", "Long side 2": "", "Groove": "",
        })
        
        blind_w = float(d.get("blind_corner_width", 1570.0))
        blind_shelf = d.get("blind_corner_shelf", True)
        
        # Left side panel
        rows.append({
            "Cut piece name": "Left side panel",
            "Wood": _dims(base_h, base_d - OUT),
            "Colour laminate": _dims(base_h, base_d - OUT),
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Right side panel
        rows.append({
            "Cut piece name": "Right side panel",
            "Wood": _dims(base_h, base_d - OUT),
            "Colour laminate": _dims(base_h, base_d - OUT),
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Top panel
        top_w = blind_w - 2*WOOD_OUT
        rows.append({
            "Cut piece name": "Top panel",
            "Wood": _dims(top_w, base_d - OUT),
            "Colour laminate": _dims(top_w, base_d - OUT),
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Bottom panel
        rows.append({
            "Cut piece name": "Bottom panel",
            "Wood": _dims(top_w, base_d - OUT),
            "Colour laminate": _dims(top_w, base_d - OUT),
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Back 6mm
        back_h_calc = base_h - 2*(WOOD_IN - groove)
        back_w_calc = blind_w - WOOD_OUT
        rows.append({
            "Cut piece name": f"Back {int(B)}mm",
            "Wood": _dims(back_h_calc, back_w_calc),
            "Colour laminate": "",
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Vertical panel
        vert_h = base_h - WOOD_IN_OUT
        vert_w = base_d - B - 50
        rows.append({
            "Cut piece name": "Vertical panel",
            "Wood": _dims(vert_h, vert_w),
            "Colour laminate": "",
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Fixed shelf
        if blind_shelf:
            shelf_w = blind_w - 2*WOOD_OUT - 150  # Approximate
            shelf_d = base_d - B - 50
            rows.append({
                "Cut piece name": "Fixed shelf",
                "Wood": _dims(shelf_w, shelf_d),
                "Colour laminate": "",
                "Laminate Color": base_color,
                "Short side 1": "",
                "Short side 2": "",
                "Long side 1": "",
                "Long side 2": "",
                "Groove": "",
            })
        
        # Tandem Bottom
        tandem_bottom_w = 350
        tandem_bottom_d = base_d - B - 50
        rows.append({
            "Cut piece name": "Tandem Bottom",
            "Wood": _dims(tandem_bottom_w, tandem_bottom_d),
            "Colour laminate": "",
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Tandem Back
        tandem_back_h = base_h - 2*(WOOD_IN - groove)
        rows.append({
            "Cut piece name": "Tandem Back",
            "Wood": _dims(tandem_back_h, 145),
            "Colour laminate": "",
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Facia
        facia_h = base_h - WOOD_IN_OUT
        facia_w = 295
        rows.append({
            "Cut piece name": "Facia",
            "Wood": _dims(facia_h, facia_w),
            "Colour laminate": _dims(facia_h, facia_w),
            "Laminate Color": facia_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Shutter
        shutter_h = base_h - WOOD_IN_OUT
        shutter_w = 485
        rows.append({
            "Cut piece name": "Shutter",
            "Wood": _dims(shutter_h, shutter_w),
            "Colour laminate": _dims(shutter_h, shutter_w),
            "Laminate Color": shutter_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Adj shelf
        rows.append({
            "Cut piece name": "Adj shelf",
            "Wood": _dims(1089, 528),
            "Colour laminate": "",
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Dummies
        rows.append({
            "Cut piece name": "Dummy",
            "Wood": _dims(670, 70),
            "Colour laminate": "",
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        rows.append({
            "Cut piece name": "Dummy",
            "Wood": _dims(690, 630),
            "Colour laminate": "",
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        rows.append({
            "Cut piece name": "Dummy",
            "Wood": _dims(base_h, 40),
            "Colour laminate": "",
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
    
    # ========== SINK UNIT ==========
    if d.get("has_sink_unit", False):
        # Add heading row for Sink Unit
        rows.append({
            "Cut piece name": "Sink unit",
            "Wood": "",
            "Colour laminate": "",
            "Laminate Color": "",
            "Short side 1": "", "Short side 2": "", "Long side 1": "", "Long side 2": "", "Groove": "",
        })
        
        sink_w = float(d.get("sink_width", 670.0))
        sink_doors = int(d.get("sink_doors", 2))
        
        # Left side panel
        rows.append({
            "Cut piece name": "Left side panel",
            "Wood": _dims(base_h, base_d - OUT),
            "Colour laminate": _dims(base_h, base_d - OUT),
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Right side panel (different material - HDHMR)
        rows.append({
            "Cut piece name": "Right side panel",
            "Wood": _dims(base_h, base_d - OUT),
            "Colour laminate": _dims(base_h, base_d - OUT),
            "Laminate Color": wall_color,  # HDHMR material
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Top panel
        top_w = sink_w - 2*WOOD_OUT
        rows.append({
            "Cut piece name": "Top panel",
            "Wood": _dims(top_w, base_d - OUT),
            "Colour laminate": _dims(top_w, base_d - OUT),
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Bottom panel
        rows.append({
            "Cut piece name": "Bottom panel",
            "Wood": _dims(top_w, base_d - OUT),
            "Colour laminate": _dims(top_w, base_d - OUT),
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Back 6mm
        back_h_calc = base_h - 2*(WOOD_IN - groove)
        back_w_calc = sink_w - WOOD_OUT
        rows.append({
            "Cut piece name": f"Back {int(B)}mm",
            "Wood": _dims(back_h_calc, back_w_calc),
            "Colour laminate": "",
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Shutters
        shutter_h = base_h - WOOD_IN_OUT
        shutter_w = (sink_w - WOOD_IN) / sink_doors
        rows.append({
            "Cut piece name": "Shutter",
            "Wood": _dims_2(shutter_h, shutter_w, sink_doors),
            "Colour laminate": _dims_2(shutter_h, shutter_w, sink_doors),
            "Laminate Color": shutter_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
    
    # ========== REGULAR BASE CABINETS ==========
    base_cabinets = int(d.get("base_cabinets", 0))
    if base_cabinets > 0:
        # Add heading row for Regular Base Cabinets
        rows.append({
            "Cut piece name": f"Regular Base Cabinets ({base_cabinets} units)",
            "Wood": "",
            "Colour laminate": "",
            "Laminate Color": "",
            "Short side 1": "", "Short side 2": "", "Long side 1": "", "Long side 2": "", "Groove": "",
        })
    
    for i in range(base_cabinets):
        cab_width = float(d.get(f"base_cab_{i}_width", 600.0))
        cab_doors = int(d.get(f"base_cab_{i}_doors", 1))
        cab_shelves = int(d.get(f"base_cab_{i}_shelves", 0))
        
        # Top
        rows.append({
            "Cut piece name": f"Base Cabinet {i+1} - Top",
            "Wood": _dims(cab_width - 2*WOOD_OUT, base_d - OUT),
            "Colour laminate": "",
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Bottom
        rows.append({
            "Cut piece name": f"Base Cabinet {i+1} - Bottom",
            "Wood": _dims(cab_width - 2*WOOD_OUT, base_d - OUT),
            "Colour laminate": "",
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Side Panels
        rows.append({
            "Cut piece name": f"Base Cabinet {i+1} - Side Panels",
            "Wood": _dims_2(base_h - WOOD_IN_OUT, base_d - OUT, 2),
            "Colour laminate": "",
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Shelves
        if cab_shelves > 0:
            shelf_depth = base_d - B - 50
            rows.append({
                "Cut piece name": f"Base Cabinet {i+1} - Shelves",
                "Wood": _dims_2(cab_width - 2*WOOD_OUT, shelf_depth, cab_shelves),
                "Colour laminate": "",
                "Laminate Color": base_color,
                "Short side 1": "",
                "Short side 2": "",
                "Long side 1": "",
                "Long side 2": "",
                "Groove": "",
            })
        
        # Back Panel
        back_h_calc = base_h - 2*(WOOD_IN - groove)
        back_w_calc = cab_width - 2*WOOD_OUT
        rows.append({
            "Cut piece name": f"Base Cabinet {i+1} - Back Panel ({int(B)}mm)",
            "Wood": _dims(back_h_calc, back_w_calc),
            "Colour laminate": "",
            "Laminate Color": base_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
    
    # ========== WALL UNITS ==========
    
    # Wall Unit-1 (Standard)
    if d.get("wall_unit_1", False):
        # Add heading row for Wall Unit-1
        rows.append({
            "Cut piece name": "Wall Unit-1 (Standard)",
            "Wood": "",
            "Colour laminate": "",
            "Laminate Color": "",
            "Short side 1": "", "Short side 2": "", "Long side 1": "", "Long side 2": "", "Groove": "",
        })
        
        wall_1_w = float(d.get("wall_unit_1_width", 1025.0))
        
        # Left side panel
        rows.append({
            "Cut piece name": "Left side panel",
            "Wood": _dims(wall_h, wall_d - OUT),
            "Colour laminate": _dims(wall_h, wall_d - OUT),
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Right side panel
        rows.append({
            "Cut piece name": "Right side panel",
            "Wood": _dims(wall_h, wall_d - OUT),
            "Colour laminate": _dims(wall_h, wall_d - OUT),
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Top panel
        top_w = wall_1_w - 2*WOOD_OUT
        rows.append({
            "Cut piece name": "Top panel",
            "Wood": _dims(top_w, wall_d - OUT),
            "Colour laminate": _dims(top_w, wall_d - OUT),
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Back panel
        back_h_calc = wall_h - 2*(WOOD_IN - groove)
        back_w_calc = wall_1_w - 2*WOOD_OUT
        rows.append({
            "Cut piece name": "Back panel",
            "Wood": _dims(back_h_calc, back_w_calc),
            "Colour laminate": "",
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Shutters
        shutter_h = wall_h - WOOD_IN_OUT
        shutter_w = wall_1_w - WOOD_IN
        rows.append({
            "Cut piece name": "Shutters",
            "Wood": _dims(shutter_h, shutter_w),
            "Colour laminate": _dims(shutter_h, shutter_w),
            "Laminate Color": shutter_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
    
    # Wall Unit-2-L Corner
    if d.get("wall_unit_2_corner", False):
        # Add heading row for Wall Unit-2-L Corner
        rows.append({
            "Cut piece name": "Wall Unit-2-L Corner",
            "Wood": "",
            "Colour laminate": "",
            "Laminate Color": "",
            "Short side 1": "", "Short side 2": "", "Long side 1": "", "Long side 2": "", "Groove": "",
        })
        
        wall_2_w = float(d.get("wall_unit_2_width", 630.0))
        
        # Left side panel
        rows.append({
            "Cut piece name": "Left side panel",
            "Wood": _dims(wall_h - 20, wall_d - OUT),
            "Colour laminate": _dims(wall_h - 20, wall_d - OUT),
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Right side panel
        rows.append({
            "Cut piece name": "Right side panel",
            "Wood": _dims(wall_h - 20, wall_d - OUT),
            "Colour laminate": _dims(wall_h - 20, wall_d - OUT),
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Top panel - L cut out
        rows.append({
            "Cut piece name": "Top panel -L cut out",
            "Wood": _dims(610, 610),
            "Colour laminate": _dims(610, 610),
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Bottom panel - L cut out
        rows.append({
            "Cut piece name": "Bottom panel -L cut out",
            "Wood": _dims(630, 630),
            "Colour laminate": _dims(630, 630),
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Back 18mm
        rows.append({
            "Cut piece name": "Back 18 mm",
            "Wood": _dims(wall_h - 20, 610),
            "Colour laminate": "",
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Back 6mm
        rows.append({
            "Cut piece name": "Back 6mm",
            "Wood": _dims(wall_h - 26, 604),
            "Colour laminate": "",
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Shutters
        shutter_h = wall_h - WOOD_IN_OUT
        shutter_w = (wall_2_w - WOOD_IN) / 2
        rows.append({
            "Cut piece name": "Shutters",
            "Wood": _dims_2(shutter_h, shutter_w, 2),
            "Colour laminate": _dims_2(shutter_h, shutter_w, 2),
            "Laminate Color": shutter_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
    
    # Wall Unit-3-Open Unit
    if d.get("wall_unit_3_open", False):
        # Add heading row for Wall Unit-3-Open Unit
        rows.append({
            "Cut piece name": "Wall Unit-3-Open Unit",
            "Wood": "",
            "Colour laminate": "",
            "Laminate Color": "",
            "Short side 1": "", "Short side 2": "", "Long side 1": "", "Long side 2": "", "Groove": "",
        })
        
        wall_3_w = float(d.get("wall_unit_3_width", 630.0))
        
        # Left side panel - 90 degree cross cut
        rows.append({
            "Cut piece name": "Left side panel- 90 degree cross cut",
            "Wood": _dims(wall_h - 20, wall_d - OUT),
            "Colour laminate": "",
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Right side panel - 90 degree cross cut
        rows.append({
            "Cut piece name": "Right side panel-90 degree cross cut",
            "Wood": _dims(wall_h - 20, wall_d - OUT),
            "Colour laminate": "",
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Top panel - L cut out
        rows.append({
            "Cut piece name": "Top panel-L cut out",
            "Wood": _dims(610, 610),
            "Colour laminate": _dims(610, 610),
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Bottom panel - L cut out
        rows.append({
            "Cut piece name": "Bottom panel -L cut out",
            "Wood": _dims(630, 630),
            "Colour laminate": "",
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Back 18mm (2 pieces)
        rows.append({
            "Cut piece name": "Back 18 mm",
            "Wood": _dims_2(wall_h - 20, 610, 2),
            "Colour laminate": "",
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
    
    # Wall Unit-4 Profile SS Unit
    if d.get("wall_unit_4_profile", False):
        # Add heading row for Wall Unit-4 Profile SS Unit
        rows.append({
            "Cut piece name": "Wall Unit-4 Profile SS Unit",
            "Wood": "",
            "Colour laminate": "",
            "Laminate Color": "",
            "Short side 1": "", "Short side 2": "", "Long side 1": "", "Long side 2": "", "Groove": "",
        })
        
        wall_4_w = float(d.get("wall_unit_4_width", 670.0))
        wall_4_doors = int(d.get("wall_unit_4_doors", 2))
        
        # Left side panel
        rows.append({
            "Cut piece name": "Left side panel",
            "Wood": _dims(wall_h, wall_d - OUT),
            "Colour laminate": _dims(wall_h, wall_d - OUT),
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Right side panel
        rows.append({
            "Cut piece name": "Right side panel",
            "Wood": _dims(wall_h, wall_d - OUT),
            "Colour laminate": _dims(wall_h, wall_d - OUT),
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Top panel
        top_w = wall_4_w - 2*WOOD_OUT
        rows.append({
            "Cut piece name": "Top panel",
            "Wood": _dims(top_w, wall_d - OUT),
            "Colour laminate": _dims(top_w, wall_d - OUT),
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Bottom panel
        rows.append({
            "Cut piece name": "Bottom panel",
            "Wood": _dims(top_w, wall_d - OUT),
            "Colour laminate": _dims(top_w, wall_d - OUT),
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "Groove",
        })
        
        # Back 6mm
        back_h_calc = wall_h - 2*(WOOD_IN - groove)
        back_w_calc = wall_4_w - 2*WOOD_OUT
        rows.append({
            "Cut piece name": "Back 6mm",
            "Wood": _dims(back_h_calc, back_w_calc),
            "Colour laminate": "",
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Adj shelf
        rows.append({
            "Cut piece name": "Adj shelf",
            "Wood": _dims(top_w - 20, wall_d - B - 50),
            "Colour laminate": "",
            "Laminate Color": wall_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Shutters (Aluminium profile shutter)
        rows.append({
            "Cut piece name": "Shutters",
            "Wood": _dims_2(wall_h - WOOD_IN_OUT, (wall_4_w - WOOD_IN) / wall_4_doors, wall_4_doors),
            "Colour laminate": _dims_2(wall_h - WOOD_IN_OUT, (wall_4_w - WOOD_IN) / wall_4_doors, wall_4_doors),
            "Laminate Color": "Aluminium profile shutter",
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
    
    # ========== LOFT ==========
    loft_shutters = int(d.get("loft_shutters", 0))
    if loft_shutters > 0:
        # Add heading row for Loft Shutters
        rows.append({
            "Cut piece name": "Loft Shutters",
            "Wood": "",
            "Colour laminate": "",
            "Laminate Color": "",
            "Short side 1": "", "Short side 2": "", "Long side 1": "", "Long side 2": "", "Groove": "",
        })
        
        loft_shutter_w = float(d.get("loft_shutter_width", 445.0))
        
        # Shutters
        rows.append({
            "Cut piece name": "Shutter",
            "Wood": _dims(loft_h, loft_shutter_w),
            "Colour laminate": _dims(loft_h, loft_shutter_w),
            "Laminate Color": loft_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Additional shutters (different sizes)
        rows.append({
            "Cut piece name": "Shutter",
            "Wood": _dims_2(loft_h, 337, 3),
            "Colour laminate": _dims_2(loft_h, 337, 3),
            "Laminate Color": loft_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        
        # Dummies
        rows.append({
            "Cut piece name": "Dummy",
            "Wood": _dims_2(550, 70, 2),
            "Colour laminate": "",
            "Laminate Color": loft_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
    
    # Loft Bottom Expo
    loft_expo_count = int(d.get("loft_bottom_expo_count", 0))
    if loft_expo_count > 0:
        # Add heading row for Loft Bottom Expo
        rows.append({
            "Cut piece name": "Loft Bottom Expo",
            "Wood": "",
            "Colour laminate": "",
            "Laminate Color": "",
            "Short side 1": "", "Short side 2": "", "Long side 1": "", "Long side 2": "", "Groove": "",
        })
        
        for i in range(loft_expo_count):
            expo_w = float(d.get(f"loft_expo_{i}_width", 2200.0))
            rows.append({
                "Cut piece name": "Loft bottom expo",
                "Wood": _dims(expo_w, base_d - OUT),
                "Colour laminate": _dims(expo_w, base_d - OUT),
                "Laminate Color": loft_color,
                "Short side 1": "",
                "Short side 2": "",
                "Long side 1": "",
                "Long side 2": "",
                "Groove": "",
            })
            
            # Additional dummies for each expo
            if expo_w >= 2000:
                rows.append({
                    "Cut piece name": "Dummy",
                    "Wood": _dims(expo_w, 80),
                    "Colour laminate": "",
                    "Laminate Color": loft_color,
                    "Short side 1": "",
                    "Short side 2": "",
                    "Long side 1": "",
                    "Long side 2": "",
                    "Groove": "",
                })
    
    # Rippers
    total_loft_width = sum([float(d.get(f"loft_expo_{i}_width", 0)) for i in range(loft_expo_count)])
    if total_loft_width > 0:
        ripper_length = total_loft_width + 2*WOOD_IN_OUT
        ripper_count = max(1, int(total_loft_width / 300))  # Approximate count
        rows.append({
            "Cut piece name": "Rippers",
            "Wood": _dims_2(ripper_length, 100, ripper_count),
            "Colour laminate": "",
            "Laminate Color": loft_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
    
    # Additional loft shutters
    if loft_shutters > 0:
        rows.append({
            "Cut piece name": "Shutter",
            "Wood": _dims_2(loft_h, 465, 2),
            "Colour laminate": _dims_2(loft_h, 465, 2),
            "Laminate Color": loft_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        rows.append({
            "Cut piece name": "Shutter",
            "Wood": _dims_2(loft_h, 330, 2),
            "Colour laminate": _dims_2(loft_h, 330, 2),
            "Laminate Color": loft_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
        })
        rows.append({
            "Cut piece name": "Shutter",
            "Wood": _dims_2(loft_h, 409, 2),
            "Colour laminate": _dims_2(loft_h, 409, 2),
            "Laminate Color": loft_color,
            "Short side 1": "",
            "Short side 2": "",
            "Long side 1": "",
            "Long side 2": "",
            "Groove": "",
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
