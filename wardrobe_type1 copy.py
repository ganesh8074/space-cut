##"2-Door Cupboard"
import streamlit as st

def form_type1(prefill=None, button_label="Save"):
    if prefill is None:
        prefill = {}
    
    outside_piece = st.selectbox(
        "Which piece comes outside?",
        options=["Side Panels", "Top Panel"],
        index=0,
        key="t1_outside_piece"
    )

    length = st.number_input("Length (mm)", min_value=300.0, value=prefill.get("length", 1800.0), step=1.0, key="t1_length")
    depth = st.number_input("Depth (mm)", min_value=300.0, value=prefill.get("depth", 600.0), step=1.0, key="t1_depth")
    height = st.number_input("Height (mm)", min_value=900.0, value=prefill.get("height", 2140.0), step=1.0, key="t1_height")
    mat_thick = st.number_input("Material Thickness (mm)", min_value=0.0, value=prefill.get("mat_thick", 18.0), step=0.1, key="t1_mt")
    inside_lam = st.number_input("Inside Laminate (mm)", min_value=0.0, value=prefill.get("inside_lam", 1.0), step=0.1, key="t1_inlam")
    outside_lam = st.number_input("Outside Laminate (mm)", min_value=0.0, value=prefill.get("outside_lam", 1.0), step=0.1, key="t1_outlam")
    plinth = st.number_input("Bottom Height (mm)", min_value=0.0, value=prefill.get("plinth", 100.0), step=1.0, key="t1_plinth")
    shelves = st.number_input("Number of Shelves", min_value=0, max_value=20, value=prefill.get("shelves", 3), step=1, key="t1_shelves")
    drawers = st.number_input("Number of Drawers", min_value=0, max_value=6, value=prefill.get("drawers", 1), step=1, key="t1_drawers")
    drawer_h = st.number_input("Drawer Height (mm)", min_value=50.0, value=prefill.get("drawer_h", 150.0), step=1.0, key="t1_drawerh")
    submitted = st.form_submit_button(button_label)
    return submitted, {
        "length": length, "depth": depth, "height": height,
        "mat_thick": mat_thick, "inside_lam": inside_lam,
        "outside_lam": outside_lam, "plinth": plinth,
        "shelves": shelves, "drawers": drawers, "drawer_h": drawer_h,
        "outside_piece": outside_piece
    }


def heading_api(title):
    st.markdown(f"""
<ul style="list-style-type: disc; padding-left: 0; margin-bottom: 0;">
  <li><strong style="font-family:'Segoe UI', sans-serif;">{title}</strong></li>
</ul>
""", unsafe_allow_html=True)

def nameing_api(name, pcs, h, w):
    def mm(val): return f"{round(val, 1)} mm"
    
    st.markdown(f"""
<style>
.material-entry {{
    display: flex;
    flex-direction: row;
    align-items: baseline;
    margin: 0 0 5px 30px; /* Moves content slightly right of the heading */
    font-family: 'Segoe UI', sans-serif;
    font-size: 15px;
}}
.label {{
    width: 280px;
    font-weight: 400;
}}
.value {{
    color: #222;
}}
</style>
<div class="material-entry">
    <div class="label">• {name}:</div>
    <div class="value">{pcs} pcs — {mm(h)} × {mm(w)}</div>
</div>
""", unsafe_allow_html=True)


def calc_type1(data):
    def mm(val): return f"{round(val,1)} mm"
    groove_thick = 7.0
    T_ALL = data["mat_thick"] + data["inside_lam"] + data["outside_lam"]
    out = []

    # Determine offset adjustments based on outside piece
    if data["outside_piece"] == "Side Panels":
        sph = data["height"] - data["outside_lam"]#side panel height
        spd = data["depth"] - data["outside_lam"]
        tpl = data["length"] - 2*T_ALL 
        tpd = data["depth"]- data["outside_lam"]
        bpl = data["length"] - 2*T_ALL
        bpd = data["depth"] - data["outside_lam"]
        bkph = data["height"] - data["plinth"] - 2*groove_thick
        bkpl = data["length"] - 2*groove_thick
        pah = data["height"] - data["plinth"] - 2*T_ALL + data["outside_lam"]
        pad = data["depth"] - groove_thick - T_ALL
        heading_api("Side Panel")
        nameing_api("Wood", 2, sph, spd)
        nameing_api("Brown Laminate", 2, sph, spd)
        nameing_api("White Laminate", 2, data["height"] - 2*T_ALL - data["plinth"] + data["outside_lam"], data["depth"] - groove_thick - data["inside_lam"])
        nameing_api("Edge Bidding", 2, data["height"], T_ALL)
        nameing_api("Edge Bidding", 2, data["depth"], T_ALL)
        
        heading_api("Top Panel")
        nameing_api("Wood", 1, tpl, tpd)
        nameing_api("Brown Laminate", 1, tpl, tpd)
        nameing_api("White Laminate", 2, (tpl - data["mat_thick"] - 2*data["inside_lam"])/2, data["depth"] - groove_thick - data["inside_lam"])
        nameing_api("Edge Bidding", 1, tpl, T_ALL)

        heading_api("Bottom Panel")
        nameing_api("Wood", 1, bpl, bpd)
        #nameing_api("Brown Laminate", 1, bpl, bpd)
        nameing_api("White Laminate", 2, (bpl - data["mat_thick"] - 2*data["inside_lam"])/2, data["depth"] - groove_thick - data["inside_lam"])
        nameing_api("Edge Bidding", 1, bpl, T_ALL)
        
        heading_api("Back Panel (6mm)")
        nameing_api("Wood", 1, bkph, bkpl)
        nameing_api("White Laminate", 2, data["height"] - 2*T_ALL - data["plinth"] + data["outside_lam"], (bpl - data["mat_thick"] - 2*data["inside_lam"])/2)
        
        heading_api("Partition")
        nameing_api("Wood", 1, pah, pad)
        nameing_api("White Laminate", 1, pah, pad)
        nameing_api("Edge Bidding", 1, pah, data["mat_thick"] + 2*data["inside_lam"])

    elif data["outside_piece"] == "Top Panel":
        sph = data["height"] - T_ALL
        spd = data["depth"] - data["outside_lam"]
        tpl = data["length"] - 2 * data["outside_lam"]
        tpd = data["depth"] - data["outside_lam"]
        bpl = data["length"] - 2*T_ALL
        bpd = data["depth"] - - data["outside_lam"]
        bkph = data["height"] - data["plinth"] - 2*groove_thick
        bkpl = data["length"] - 2*groove_thick
        pah = data["height"] - data["plinth"] - 2*T_ALL
        pad = data["depth"]  - T_ALL - groove_thick
           
    if data["shelves"] > 0:
        shelf_len = ((data["length"] - 3*T_ALL) / 2) + 1
        shelf_dep = data["depth"] - T_ALL - groove_thick
        heading_api("Shelves")
        nameing_api("Wood", data['shelves'], shelf_len, shelf_dep)
        nameing_api("White Laminate", 2 * data['shelves'], shelf_len, shelf_dep)
        nameing_api("Edge Bidding", data['shelves'], shelf_len, data["mat_thick"] + 2*data["inside_lam"])

    door_h = data["height"] - data["plinth"] - (2 * data["outside_lam"])
    door_w = (data["length"] / 2) - (2 * data["outside_lam"])
    heading_api("Doors")
    nameing_api("Wood", 2, door_h, door_w)
    nameing_api("Brown Laminate", 2, door_h, door_w)
    nameing_api("White Laminate", 2, door_h, door_w)
    nameing_api("Edge Bidding", 4, door_h, T_ALL)
    nameing_api("Edge Bidding", 4, door_w, T_ALL)

    if data["drawers"] > 0:
        drawer_side = data["depth"] - 2*T_ALL - groove_thick
        heading_api("Drawers")
        nameing_api("Wood Side", data['drawers']*2, drawer_side, (data['drawer_h'] - 2*T_ALL))
        nameing_api("Wood Back", data['drawers'], (shelf_len - 4*T_ALL), data['drawer_h'] - 2*T_ALL)
        nameing_api("Wood Front", data['drawers'], (shelf_len - 4*T_ALL), (data['drawer_h'] - 2*T_ALL)/2)
        nameing_api("Wood Bottoms - (6mm)", data['drawers'], (shelf_len - 4*T_ALL), drawer_side)
        nameing_api("Wood Side Extra Pieces ", data['drawers']*3, drawer_side, (data['drawer_h'] - T_ALL))
        nameing_api("Wood Front Expo Pieces ", data['drawers'], (shelf_len - 1*T_ALL), (data['drawer_h'] - T_ALL))
       
        nameing_api("White Laminate Side", data['drawers']*4, drawer_side, (data['drawer_h'] - 2*T_ALL))
        nameing_api("White Laminate Back", data['drawers'], (shelf_len - 4*T_ALL), data['drawer_h'] - 2*T_ALL)
        nameing_api("White Laminate Front", data['drawers'], (shelf_len - 4*T_ALL), (data['drawer_h'] - 2*T_ALL)/2)
        nameing_api("White Laminate Bottoms - (6mm)", data['drawers']*2, (shelf_len - 4*T_ALL), drawer_side)
        nameing_api("White Laminate Side Extra Pieces ", data['drawers']*3, drawer_side, (data['drawer_h'] - T_ALL))
        nameing_api("White Laminate Front Expo Pieces ", data['drawers']*2, (shelf_len - 1*T_ALL), (data['drawer_h'] - T_ALL))

        nameing_api("Edge Bidding Side", data['drawers']*4, drawer_side, data["mat_thick"] + 2*data["inside_lam"])
        nameing_api("Edge Bidding Back", data['drawers'], (shelf_len - 4*T_ALL), data["mat_thick"] + data["inside_lam"])
        nameing_api("Edge Bidding Front", data['drawers'], (shelf_len - 4*T_ALL), data["mat_thick"] + data["inside_lam"])
        nameing_api("Edge Bidding Side Extra Pieces Down", data['drawers']*3, drawer_side, data["mat_thick"] + data["inside_lam"])
        nameing_api("Edge Bidding Side Extra Pieces Front", data['drawers']*3, (data['drawer_h'] - T_ALL), data["mat_thick"] + data["inside_lam"])

        nameing_api("Edge Bidding Front Expo Pieces Top ", data['drawers']*2, (shelf_len - 1*T_ALL), data["mat_thick"] + 2*data["inside_lam"])
        nameing_api("Edge Bidding Front Expo Pieces Side", data['drawers']*2, (data['drawer_h'] - T_ALL), data["mat_thick"] + 2*data["inside_lam"])
    
        heading_api("Bottom")
        nameing_api("Wood", 1, data['length'] - 2*T_ALL + 2*data["inside_lam"], data["plinth"])
        nameing_api("Brown Laminate", 1, data['length'] - 2*T_ALL + 2*data["inside_lam"], data["plinth"])
        nameing_api("Edge Bidding", 1, data['length'] - 2*T_ALL + 2*data["inside_lam"], T_ALL)          



    # out.append(f"Side Panels: 2 pcs — {mm(sph)} × {mm(spd)}")
    # out.append(f"Top Panel: 1 pc — {mm(tpl)} × {mm(tpd)}")
    # out.append(f"Bottom Panel: 1 pc — {mm(bpl)} × {mm(bpd)}")
    # out.append(f"Back Panel (6mm): 1 pc — {mm(bkph)} × {mm(bkpl)}")
    # out.append(f"Partition: 1 pcs — {mm(pah)} × {mm(pad)}")

    #  if data["shelves"] > 0:
    #     shelf_len = ((data["length"] - 3*T_ALL) / 2) + 1
    #     shelf_dep = data["depth"] - T_ALL - groove_thick
    #     out.append(f"Shelves: {data['shelves']} pcs — {mm(shelf_len)} × {mm(shelf_dep)}")

    # door_h = data["height"] - data["plinth"] - (2 * data["outside_lam"])
    # door_w = (data["length"] / 2) - (2 * data["outside_lam"])
    # out.append(f"Doors (Normal): 2 pcs — {mm(door_h)} × {mm(door_w)}")


    # if data["drawers"] > 0:
    #     drawer_side = data["depth"] - 2*T_ALL - groove_thick
    #     out.append(f"Drawer Sides: {data['drawers']*2} pcs — {mm(drawer_side)} × {mm(data['drawer_h'] - 2*T_ALL)}")
    #     out.append(f"Drawer Back: {data['drawers']} pcs — {mm(shelf_len - 4*T_ALL)} × {mm(data['drawer_h'] - 2*T_ALL)}")
    #     out.append(f"Drawer Front: {data['drawers']} pcs — {mm(shelf_len - 4*T_ALL) } × {mm((data['drawer_h'] - 2*T_ALL)/2)}")
    #     out.append(f"Drawer Bottoms - (6mm): {data['drawers']} pcs — {mm(shelf_len - 4*T_ALL)} × {mm(drawer_side)}")
    #     out.append(f"Drawer Side Extra Pieces: {data['drawers']*3} pcs — {mm(drawer_side) } × {mm(data['drawer_h'] - T_ALL)}")
    #     out.append(f"Drawer Front Expo Pieces: {data['drawers']} pcs — {mm(shelf_len - 1*T_ALL) } × {mm(data['drawer_h'] - T_ALL)}")
       
    # out.append(f"Front Expo Pieces on Down: 1 pcs — {mm(data['length'] - 2*T_ALL)} × {mm(data["plinth"] - data["outside_lam"])}")



    return out
