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

def create_row(description, height, width, qty, material, long1="", long2="", short1="", short2="", groove=""):
    """Helper to create a row in the new standard format"""
    # Format numbers to remove trailing zeros
    def clean_number(val):
        if not val:
            return 0
        rounded = round(val, 1)
        # Convert to int if it's a whole number
        return int(rounded) if rounded == int(rounded) else rounded
    
    return {
        "Description": description,
        "Height": clean_number(height),
        "Width": clean_number(width),
        "Qty": qty,
        "Material": material,
        "Long side 1": long1,
        "Long side 2": long2,
        "Short side 1": short1,
        "Short side 2": short2,
        "Groove": groove,
    }

def create_heading_row(title):
    """Helper to create a heading row (for section titles)"""
    return {
        "Description": title,
        "Height": "",
        "Width": "",
        "Qty": "",
        "Material": "",
        "Long side 1": "",
        "Long side 2": "",
        "Short side 1": "",
        "Short side 2": "",
        "Groove": "",
    }

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
        rows.append(create_heading_row(heading))
    
    # ========== BPO (BOTTLE PULL OUT) ==========
    if d.get("has_bpo", False):
        bpo_w = float(d.get("bpo_width", 1025.0))
        
        # Left side panel
        rows.append(create_row(
            "Left side panel",
            base_h, base_d - OUT, 1,
            f"18 mm BWP PLY {base_color}",
            long1="2*22 107 - LU",
            groove="Groove on Long side 2"
        ))
        
        # Right side panel
        rows.append(create_row(
            "Right side panel",
            base_h, base_d - OUT, 1,
            f"18 mm BWP PLY {base_color}",
            long1="2*22 107 - LU",
            groove="Groove on Long side 2"
        ))
        
        # Top Panel
        top_w = bpo_w - 2*WOOD_OUT
        rows.append(create_row(
            "Top Panel",
            top_w, base_d - OUT, 1,
            f"18 mm BWP PLY {base_color}",
            long1="2*22 107 - LU",
            groove="Groove"
        ))
        
        # Bottom panel
        rows.append(create_row(
            "Bottom panel",
            top_w, base_d, 1,
            f"18 mm BWP PLY {base_color}",
            long1="2*22 107 - LU",
            groove="Groove"
        ))
        
        # Back 6mm
        back_h_calc = base_h - 2*(WOOD_IN - groove)
        back_w_calc = bpo_w - WOOD_OUT
        rows.append(create_row(
            f"Back ({int(B)}mm)",
            back_h_calc, back_w_calc, 2,
            f"{int(B)} mm BWP PLY {base_color}"
        ))
        
        # Vertical panel
        vert_h = base_h - WOOD_IN_OUT
        vert_w = base_d - B - 50
        rows.append(create_row(
            "Vertical panel",
            vert_h, vert_w, 1,
            f"18 mm BWP PLY {base_color}",
            long1="2*22 107 - LU"
        ))
    
    # ========== TANDEM ==========
    if d.get("has_tandem", False):
        tandem_w = float(d.get("tandem_width", 600.0))
        tandem_count = int(d.get("tandem_count", 1))
        tandem_type = d.get("tandem_type", "2-door")
        
        # Tandem Bottom
        tandem_bottom_w = tandem_w - 2*WOOD_OUT
        tandem_bottom_d = base_d - B - 50
        rows.append(create_row(
            "Tandem Bottom",
            tandem_bottom_w, tandem_bottom_d, tandem_count,
            f"18 mm BWP PLY {base_color}"
        ))
        
        # Tandem Back (different sizes based on door count)
        tandem_back_h = base_h - 2*(WOOD_IN - groove)
        if tandem_type == "2-door":
            # Two sizes: 638x68 (2 pieces) and 638x145 (1 piece)
            rows.append(create_row(
                "Tandem Back",
                tandem_back_h, 68, 2,
                f"18 mm BWP PLY {base_color}",
                short1="0.8*22 FB", short2="0.8*22 FB", long1="0.8*22 FB", long2="0.8*22 FB"
            ))
            rows.append(create_row(
                "Tandem Back",
                tandem_back_h, 145, 1,
                f"18 mm BWP PLY {base_color}",
                short1="0.8*22 FB", short2="0.8*22 FB", long1="0.8*22 FB", long2="0.8*22 FB"
            ))
        else:  # 3-door
            # Similar logic for 3-door configuration
            rows.append(create_row(
                "Tandem Back",
                tandem_back_h, 68, 3,
                f"18 mm BWP PLY {base_color}",
                short1="0.8*22 FB", short2="0.8*22 FB", long1="0.8*22 FB", long2="0.8*22 FB"
            ))
        
        # Facia for tandems
        facia_h = base_h - WOOD_IN_OUT
        if tandem_type == "2-door":
            facia_w_1 = (tandem_w - WOOD_IN) / 2
            rows.append(create_row(
                "Facia",
                facia_h, facia_w_1, 2,
                f"18 mm HDHMR {facia_color}",
                long1="2*22 107 - LU", long2="2*22 107 - LU", short1="2*22 107 - LU", short2="2*22 107 - LU"
            ))
            facia_w_2 = tandem_w - WOOD_IN - facia_w_1
            rows.append(create_row(
                "Facia",
                facia_h, facia_w_2, 1,
                f"18 mm HDHMR {facia_color}",
                long1="2*22 107 - LU", long2="2*22 107 - LU", short1="2*22 107 - LU", short2="2*22 107 - LU"
            ))
        else:  # 3-door
            facia_w = (tandem_w - WOOD_IN) / 3
            rows.append(create_row(
                "Facia",
                facia_h, facia_w, 3,
                f"18 mm HDHMR {facia_color}",
                long1="2*22 107 - LU", long2="2*22 107 - LU", short1="2*22 107 - LU", short2="2*22 107 - LU"
            ))
        
        # Shutter for tandem
        shutter_h = base_h - WOOD_IN_OUT
        shutter_w = tandem_w / (3 if tandem_type == "3-door" else 2)
        rows.append(create_row(
            "Shutter",
            shutter_h, shutter_w, 1,
            f"18 mm HDHMR {shutter_color}",
            long1="2*22 107 - LU", long2="2*22 107 - LU", short1="2*22 107 - LU", short2="2*22 107 - LU"
        ))
        
        # Dummy
        rows.append(create_row(
            "Dummy",
            base_h, 50, 1,
            f"18 mm HDHMR {base_color}",
            short1="0.8* 22 107 -LU"
        ))
    
    # ========== BLIND CORNER UNIT ==========
    if d.get("has_blind_corner", False):
        # Add heading row for Blind Corner Unit
        rows.append(create_heading_row("Blind corner unit"))
        
        blind_w = float(d.get("blind_corner_width", 1570.0))
        blind_shelf = d.get("blind_corner_shelf", True)
        
        # Left side panel
        rows.append(create_row(
            "Left side panel",
            base_h, base_d - OUT, 1,
            f"18 mm BWP PLY {base_color}",
            long1="2*22 107 - LU",
            groove="Groove on Long side 2"
        ))
        
        # Right side panel
        rows.append(create_row(
            "Right side panel",
            base_h, base_d - OUT, 1,
            f"18 mm BWP PLY {base_color}",
            long1="2*22 107 - LU",
            groove="Groove on Long side 2"
        ))
        
        # Top panel
        top_w = blind_w - 2*WOOD_OUT
        rows.append(create_row(
            "Top panel",
            top_w, base_d - OUT, 1,
            f"18 mm BWP PLY {base_color}",
            long1="2*22 107 - LU",
            groove="Groove"
        ))
        
        # Bottom panel
        rows.append(create_row(
            "Bottom panel",
            top_w, base_d, 1,
            f"18 mm BWP PLY {base_color}",
            long1="2*22 107 - LU",
            groove="Groove"
        ))
        
        # Back 6mm
        back_h_calc = base_h - 2*(WOOD_IN - groove)
        back_w_calc = blind_w - WOOD_OUT
        rows.append(create_row(
            f"Back ({int(B)}mm)",
            back_h_calc, back_w_calc, 1,
            f"{int(B)} mm BWP PLY {base_color}"
        ))
        
        # Vertical panel
        vert_h = base_h - WOOD_IN_OUT
        vert_w = base_d - B - 50
        rows.append(create_row(
            "Vertical panel",
            vert_h, vert_w, 1,
            f"18 mm BWP PLY {base_color}",
            long1="2*22 107 - LU"
        ))
        
        # Fixed shelf
        if blind_shelf:
            shelf_w = blind_w - 2*WOOD_OUT - 150  # Approximate
            shelf_d = base_d - B - 50
            rows.append(create_row(
                "Fixed shelf",
                shelf_w, shelf_d, 1,
                f"18 mm BWP PLY {base_color}",
                long1="2*22 107 - LU"
            ))
        
        # Tandem Bottom
        tandem_bottom_w = 350
        tandem_bottom_d = base_d - B - 50
        rows.append(create_row(
            "Tandem Bottom",
            tandem_bottom_w, tandem_bottom_d, 1,
            f"18 mm BWP PLY {base_color}"
        ))
        
        # Tandem Back
        tandem_back_h = base_h - 2*(WOOD_IN - groove)
        rows.append(create_row(
            "Tandem Back",
            tandem_back_h, 145, 1,
            f"18 mm BWP PLY {base_color}",
            short1="0.8*22 FB", short2="0.8*22 FB", long1="0.8*22 FB", long2="0.8*22 FB"
        ))
        
        # Facia
        facia_h = base_h - WOOD_IN_OUT
        facia_w = 295
        rows.append(create_row(
            "Facia",
            facia_h, facia_w, 1,
            f"18 mm HDHMR {facia_color}",
            long1="2*22 107 - LU", long2="2*22 107 - LU", short1="2*22 107 - LU", short2="2*22 107 - LU"
        ))
        
        # Shutter
        shutter_h = base_h - WOOD_IN_OUT
        shutter_w = 485
        rows.append(create_row(
            "Shutter",
            shutter_h, shutter_w, 1,
            f"18 mm HDHMR {shutter_color}",
            long1="2*22 107 - LU", long2="2*22 107 - LU", short1="2*22 107 - LU", short2="2*22 107 - LU"
        ))
        
        # Adj shelf
        rows.append(create_row(
            "Adj shelf",
            1089, 528, 1,
            f"18 mm BWP PLY {base_color}",
            short1="0.8*22 FB"
        ))
        
        # Dummies
        rows.append(create_row(
            "Dummy",
            670, 70, 1,
            f"18 mm BWP PLY {base_color}",
            short1="0.8*22 FB"
        ))
        rows.append(create_row(
            "Dummy",
            690, 630, 1,
            f"18 mm BWP PLY {base_color}",
            short1="0.8*22 FB"
        ))
        rows.append(create_row(
            "Dummy",
            base_h, 40, 1,
            f"18 mm HDHMR {base_color}",
            long1="2*22 107 - LU"
        ))
    
    # ========== SINK UNIT ==========
    if d.get("has_sink_unit", False):
        # Add heading row for Sink Unit
        rows.append(create_heading_row("Sink unit"))
        
        sink_w = float(d.get("sink_width", 670.0))
        sink_doors = int(d.get("sink_doors", 2))
        
        # Left side panel
        rows.append(create_row(
            "Left side panel",
            base_h, base_d - OUT, 1,
            f"18 mm BWP PLY {base_color}",
            long1="2*22 107 - LU",
            groove="Groove on Long side 2"
        ))
        
        # Right side panel (different material - HDHMR)
        rows.append(create_row(
            "Right side panel",
            base_h + 100, base_d - OUT, 1,
            f"18 mm HDHMR {wall_color}",
            long1="2*22 107 - LU", short1="0.8*22 255 - LU", short2="0.8*22 255 - LU", long2="0.8*22 255 - LU",
            groove="Groove"
        ))
        
        # Top panel
        top_w = sink_w - 2*WOOD_OUT
        rows.append(create_row(
            "Top panel",
            top_w, base_d - OUT, 1,
            f"18 mm BWP PLY {base_color}",
            long1="2*22 107 - LU",
            groove="Groove"
        ))
        
        # Bottom panel
        rows.append(create_row(
            "Bottom panel",
            top_w, base_d, 1,
            f"18 mm BWP PLY {base_color}",
            long1="2*22 107 - LU",
            groove="Groove"
        ))
        
        # Back 6mm
        back_h_calc = base_h - 2*(WOOD_IN - groove)
        back_w_calc = sink_w - WOOD_OUT
        rows.append(create_row(
            f"Back ({int(B)}mm)",
            back_h_calc, back_w_calc, 1,
            f"{int(B)} mm BWP PLY {base_color}"
        ))
        
        # Shutters
        shutter_h = base_h - WOOD_IN_OUT
        shutter_w = (sink_w - WOOD_IN) / sink_doors
        rows.append(create_row(
            "Shutter",
            shutter_h, shutter_w, sink_doors,
            f"18 mm HDHMR {shutter_color}",
            long1="2*22 107 - LU", long2="2*22 107 - LU", short1="2*22 107 - LU", short2="2*22 107 - LU"
        ))
    
    # ========== REGULAR BASE CABINETS ==========
    base_cabinets = int(d.get("base_cabinets", 0))
    if base_cabinets > 0:
        # Add heading row for Regular Base Cabinets
        rows.append(create_heading_row(f"Regular Base Cabinets ({base_cabinets} units)"))
    
    for i in range(base_cabinets):
        cab_width = float(d.get(f"base_cab_{i}_width", 600.0))
        cab_doors = int(d.get(f"base_cab_{i}_doors", 1))
        cab_shelves = int(d.get(f"base_cab_{i}_shelves", 0))
        
        # Top
        rows.append(create_row(
            f"Base Cabinet {i+1} - Top",
            cab_width - 2*WOOD_OUT, base_d - OUT, 1,
            f"18 mm BWP PLY {base_color}",
            long1="2*22 107 - LU",
            groove="Groove"
        ))
        
        # Bottom
        rows.append(create_row(
            f"Base Cabinet {i+1} - Bottom",
            cab_width - 2*WOOD_OUT, base_d, 1,
            f"18 mm BWP PLY {base_color}",
            long1="2*22 107 - LU",
            groove="Groove"
        ))
        
        # Side Panels
        rows.append(create_row(
            f"Base Cabinet {i+1} - Side Panels",
            base_h - WOOD_IN_OUT, base_d - OUT, 2,
            f"18 mm BWP PLY {base_color}",
            long1="2*22 107 - LU",
            groove="Groove"
        ))
        
        # Shelves
        if cab_shelves > 0:
            shelf_depth = base_d - B - 50
            rows.append(create_row(
                f"Base Cabinet {i+1} - Shelves",
                cab_width - 2*WOOD_OUT, shelf_depth, cab_shelves,
                f"18 mm BWP PLY {base_color}",
                short1="0.8*22 FB"
            ))
        
        # Back Panel
        back_h_calc = base_h - 2*(WOOD_IN - groove)
        back_w_calc = cab_width - 2*WOOD_OUT
        rows.append(create_row(
            f"Base Cabinet {i+1} - Back Panel ({int(B)}mm)",
            back_h_calc, back_w_calc, 1,
            f"{int(B)} mm BWP PLY {base_color}"
        ))
    
    # ========== WALL UNITS ==========
    
    # Wall Unit-1 (Standard)
    if d.get("wall_unit_1", False):
        # Add heading row for Wall Unit-1
        rows.append(create_heading_row("Wall Unit-1 (Standard)"))
        
        wall_1_w = float(d.get("wall_unit_1_width", 1025.0))
        
        # Left side panel
        rows.append(create_row(
            "Left side panel",
            wall_h, wall_d - OUT, 1,
            f"18 mm HDHMR {wall_color}",
            long1="2*22 255 - LU", short1="0.8*22 255 - LU", short2="0.8*22 255 - LU"
        ))
        
        # Right side panel
        rows.append(create_row(
            "Right side panel",
            wall_h, wall_d - OUT, 1,
            f"18 mm HDHMR {wall_color}",
            long1="2*22 255 - LU", short1="0.8*22 255 - LU", short2="0.8*22 255 - LU"
        ))
        
        # Top panel
        top_w = wall_1_w - 2*WOOD_OUT
        rows.append(create_row(
            "Top panel",
            top_w, wall_d - OUT, 1,
            f"18 mm HDHMR {wall_color}",
            long1="2*22 255 - LU", short1="0.8*22 255 - LU", short2="0.8*22 255 - LU"
        ))
        
        # Back panel
        back_h_calc = wall_h - 2*(WOOD_IN - groove)
        back_w_calc = wall_1_w - 2*WOOD_OUT
        rows.append(create_row(
            "Back panel",
            back_h_calc, back_w_calc, 1,
            f"18 mm HDHMR {wall_color}",
            short1="0.8*22 FB", short2="0.8*22 FB", long1="0.8*22 FB", long2="0.8*22 FB"
        ))
        
        # Shutters
        shutter_h = wall_h - WOOD_IN_OUT
        shutter_w = wall_1_w - WOOD_IN
        rows.append(create_row(
            "Shutters",
            shutter_h, shutter_w, 1,
            f"18 mm HDHMR {shutter_color}",
            long1="2*22 255 - LU", long2="2*22 255 - LU", short1="2*22 255 - LU", short2="2*22 255 - LU"
        ))
    
    # Wall Unit-2-L Corner
    if d.get("wall_unit_2_corner", False):
        # Add heading row for Wall Unit-2-L Corner
        rows.append(create_heading_row("Wall Unit-2-L Corner"))
        
        wall_2_w = float(d.get("wall_unit_2_width", 630.0))
        
        # Left side panel
        rows.append(create_row(
            "Left side panel",
            wall_h - 20, wall_d - OUT, 1,
            f"18 mm HDHMR {wall_color}",
            long1="2*22 255 - LU", short1="0.8*22 255 - LU", short2="0.8*22 255 - LU"
        ))
        
        # Right side panel
        rows.append(create_row(
            "Right side panel",
            wall_h - 20, wall_d - OUT, 1,
            f"18 mm HDHMR {wall_color}",
            long1="2*22 255 - LU", short1="0.8*22 255 - LU", short2="0.8*22 255 - LU",
            groove="Groove"
        ))
        
        # Top panel - L cut out
        rows.append(create_row(
            "Top panel -L cut out",
            610, 610, 1,
            f"18 mm MR PLY {base_color}",
            long1="2*22 255 - LU", short1="0.8*22 255 - LU", short2="0.8*22 255 - LU",
            groove="Groove"
        ))
        
        # Bottom panel - L cut out
        rows.append(create_row(
            "Bottom panel -L cut out",
            630, 630, 1,
            f"18 mm HDHMR {wall_color}",
            long1="2*22 255 - LU", short1="0.8*22 255 - LU", short2="0.8*22 255 - LU", long2="0.8*22 255 - LU",
            groove="Groove"
        ))
        
        # Back 18mm
        rows.append(create_row(
            "Back 18 mm",
            wall_h - 20, 610, 1,
            f"18 mm MR PLY {base_color}",
            groove="Groove"
        ))
        
        # Back 6mm
        rows.append(create_row(
            "Back 6mm",
            wall_h - 26, 604, 1,
            f"6 mm MR PLY {base_color}"
        ))
        
        # Shutters
        shutter_h = wall_h - WOOD_IN_OUT
        shutter_w = (wall_2_w - WOOD_IN) / 2
        rows.append(create_row(
            "Shutters",
            shutter_h, shutter_w, 2,
            f"18 mm HDHMR {shutter_color}",
            long1="2*22 255 - LU", long2="2*22 255 - LU", short1="2*22 255 - LU", short2="2*22 255 - LU"
        ))
    
    # Wall Unit-3-Open Unit
    if d.get("wall_unit_3_open", False):
        # Add heading row for Wall Unit-3-Open Unit
        rows.append(create_heading_row("Wall Unit-3-Open Unit"))
        
        wall_3_w = float(d.get("wall_unit_3_width", 630.0))
        
        # Left side panel - 90 degree cross cut
        rows.append(create_row(
            "Left side panel- 90 degree cross cut",
            wall_h - 115, wall_d - 37, 1,
            f"18 mm HDHMR {wall_color}",
            long1="2*22 255 - LU", short1="0.8*22 255 - LU", short2="0.8*22 255 - LU"
        ))
        
        # Right side panel - 90 degree cross cut
        rows.append(create_row(
            "Right side panel-90 degree cross cut",
            wall_h - 115, wall_d - 37, 1,
            f"18 mm HDHMR {wall_color}",
            long1="2*22 255 - LU", short1="0.8*22 255 - LU", short2="0.8*22 255 - LU"
        ))
        
        # Top panel - L cut out
        rows.append(create_row(
            "Top panel-L cut out",
            610, 610, 1,
            f"18 mm HDHMR {wall_color}",
            long1="2*22 255 - LU", short1="0.8*22 255 - LU", short2="0.8*22 255 - LU"
        ))
        
        # Bottom panel - L cut out
        rows.append(create_row(
            "Bottom panel -L cut out",
            630, 630, 1,
            f"18 mm HDHMR {wall_color}",
            long1="2*22 255 - LU", short1="0.8*22 255 - LU", short2="0.8*22 255 - LU", long2="0.8*22 255 - LU"
        ))
        
        # Back 18mm (2 pieces)
        rows.append(create_row(
            "Back 18 mm",
            wall_h - 20, 610, 1,
            f"18 mm HDHMR {wall_color}"
        ))
        rows.append(create_row(
            "Back 18 mm",
            wall_h - 20, 590, 1,
            f"18 mm HDHMR {wall_color}"
        ))
    
    # Wall Unit-4 Profile SS Unit
    if d.get("wall_unit_4_profile", False):
        # Add heading row for Wall Unit-4 Profile SS Unit
        rows.append(create_heading_row("Wall Unit-4 Profile SS Unit"))
        
        wall_4_w = float(d.get("wall_unit_4_width", 670.0))
        wall_4_doors = int(d.get("wall_unit_4_doors", 2))
        
        # Left side panel
        rows.append(create_row(
            "Left side panel",
            wall_h + 375, wall_d - OUT, 1,
            f"18 mm HDHMR {wall_color}",
            long1="2*22 255 - LU", short1="0.8*22 255 - LU", short2="0.8*22 255 - LU",
            groove="Groove"
        ))
        
        # Right side panel
        rows.append(create_row(
            "Right side panel",
            wall_h + 375, wall_d - OUT, 1,
            f"18 mm HDHMR {wall_color}",
            long1="2*22 255 - LU", short1="0.8*22 255 - LU", short2="0.8*22 255 - LU",
            groove="Groove"
        ))
        
        # Top panel
        top_w = wall_4_w - 2*WOOD_OUT
        rows.append(create_row(
            "Top panel",
            top_w, wall_d - OUT, 1,
            f"18 mm MR PLY {base_color}",
            long1="2*22 255 - LU", short1="0.8*22 255 - LU", short2="0.8*22 255 - LU",
            groove="Groove"
        ))
        
        # Bottom panel
        rows.append(create_row(
            "Bottom panel",
            top_w, wall_d - OUT, 1,
            f"18 mm HDHMR {wall_color}",
            long1="2*22 255 - LU", short1="0.8*22 255 - LU", short2="0.8*22 255 - LU",
            groove="Groove"
        ))
        
        # Back 6mm
        back_h_calc = wall_h - 2*(WOOD_IN - groove) + 375
        back_w_calc = wall_4_w - 2*WOOD_OUT
        rows.append(create_row(
            "Back 6mm",
            back_h_calc, back_w_calc, 1,
            f"6 mm MR PLY {base_color}"
        ))
        
        # Adj shelf
        rows.append(create_row(
            "Adj shelf",
            top_w - 20, wall_d - B - 47, 1,
            f"18 mm MR PLY {base_color}",
            short1="0.8*22 FB"
        ))
        
        # Shutters (Aluminium profile shutter)
        shutter_w = (wall_4_w - WOOD_IN) / wall_4_doors
        rows.append(create_row(
            "Shutters",
            wall_h - WOOD_IN_OUT + 375, shutter_w, wall_4_doors,
            "Aluminium profile shutter"
        ))
    
    # ========== LOFT ==========
    loft_shutters = int(d.get("loft_shutters", 0))
    if loft_shutters > 0:
        # Add heading row for Loft
        rows.append(create_heading_row("Loft"))
        
        loft_shutter_w = float(d.get("loft_shutter_width", 445.0))
        
        # Shutters
        rows.append(create_row(
            "Shutter",
            loft_h, loft_shutter_w, 1,
            f"18 mm HDHMR {loft_color}",
            long1="2*22 255 - LU", long2="2*22 255 - LU", short1="2*22 255 - LU", short2="2*22 255 - LU"
        ))
        
        # Additional shutters (different sizes)
        rows.append(create_row(
            "Shutter",
            loft_h, 337, 3,
            f"18 mm HDHMR {loft_color}",
            long1="2*22 255 - LU", long2="2*22 255 - LU", short1="2*22 255 - LU", short2="2*22 255 - LU"
        ))
        
        # Dummies
        rows.append(create_row(
            "Dummy",
            550, 70, 2,
            f"18 mm HDHMR {loft_color}",
            short1="0.8*22 255 - LU"
        ))
    
    # Loft Bottom Expo
    loft_expo_count = int(d.get("loft_bottom_expo_count", 0))
    if loft_expo_count > 0:
        for i in range(loft_expo_count):
            expo_w = float(d.get(f"loft_expo_{i}_width", 2200.0))
            rows.append(create_row(
                "Loft bottom expo",
                expo_w, base_d, 1,
                f"18 mm HDHMR {loft_color}",
                long1="2*22 255 - LU", short1="0.8*22 255 - LU", short2="0.8*22 255 - LU", long2="0.8*22 255 - LU"
            ))
            
            # Additional dummies for each expo
            if expo_w >= 2000:
                rows.append(create_row(
                    "Dummy",
                    expo_w, 80, 1,
                    f"18 mm HDHMR {loft_color}",
                    short1="0.8*22 255 - LU"
                ))
    
    # Rippers
    total_loft_width = sum([float(d.get(f"loft_expo_{i}_width", 0)) for i in range(loft_expo_count)])
    if total_loft_width > 0:
        ripper_length = total_loft_width + 2*WOOD_IN_OUT
        ripper_count = max(1, int(total_loft_width / 300))  # Approximate count
        rows.append(create_row(
            "Rippers",
            ripper_length, 100, ripper_count,
            f"18 mm MR PLY {base_color}",
            short1="0.8*22 FB", short2="0.8*22 FB"
        ))
    
    # Additional loft shutters
    if loft_shutters > 0:
        rows.append(create_row(
            "Shutter",
            loft_h, 465, 2,
            f"18 mm HDHMR {loft_color}",
            long1="2*22 255 - LU", long2="2*22 255 - LU", short1="2*22 255 - LU", short2="2*22 255 - LU"
        ))
        rows.append(create_row(
            "Shutter",
            loft_h, 330, 2,
            f"18 mm HDHMR {loft_color}",
            long1="2*22 255 - LU", long2="2*22 255 - LU", short1="2*22 255 - LU", short2="2*22 255 - LU"
        ))
        rows.append(create_row(
            "Shutter",
            loft_h, 409, 2,
            f"18 mm HDHMR {loft_color}",
            long1="2*22 255 - LU", long2="2*22 255 - LU", short1="2*22 255 - LU", short2="2*22 255 - LU"
        ))
    
    # Add SLNO to each row
    for idx, row in enumerate(rows, start=1):
        row["SLNO"] = idx
    
    df = pd.DataFrame(rows, columns=[
        "SLNO",
        "Description",
        "Height",
        "Width",
        "Qty",
        "Material",
        "Long side 1",
        "Long side 2",
        "Short side 1",
        "Short side 2",
        "Groove",
    ])
    return df
