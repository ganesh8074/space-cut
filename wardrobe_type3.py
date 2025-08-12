#"3-Door Cupboard"
import streamlit as st

def form_type3(prefill=None, button_label="Save"):
    if prefill is None:
        prefill = {}
    length = st.number_input("Length (mm)", min_value=300.0, value=prefill.get("length", 2100.0), step=1.0, key="t2_length")
    depth = st.number_input("Depth (mm)", min_value=300.0, value=prefill.get("depth", 600.0), step=1.0, key="t2_depth")
    height = st.number_input("Height (mm)", min_value=900.0, value=prefill.get("height", 2140.0), step=1.0, key="t2_height")
    mat_thick = st.number_input("Material Thickness (mm)", min_value=0.0, value=prefill.get("mat_thick", 18.0), step=0.5, key="t2_mt")
    inside_lam = st.number_input("Inside Laminate (mm)", min_value=0.0, value=prefill.get("inside_lam", 1.0), step=0.5, key="t2_inlam")
    outside_lam = st.number_input("Outside Laminate (mm)", min_value=0.0, value=prefill.get("outside_lam", 1.0), step=0.5, key="t2_outlam")
    plinth = st.number_input("Bottom Height (mm)", min_value=0.0, value=prefill.get("plinth", 100.0), step=1.0, key="t2_plinth")
    left_shelves = st.number_input("Number of Left Shelves", min_value=0, max_value=20, value=prefill.get("left_shelves", 2), step=1, key="tl2_shelves")
    right_shelves = st.number_input("Number of Right Shelves", min_value=0, max_value=20, value=prefill.get("right_shelves", 4), step=1, key="tr2_shelves")
    drawers = st.number_input("Number of Drawers", min_value=0, max_value=6, value=prefill.get("drawers", 2), step=1, key="t2_drawers")
    drawer_h = st.number_input("Drawer Height (mm)", min_value=50.0, value=prefill.get("drawer_h", 150.0), step=1.0, key="t2_drawerh")
    submitted = st.form_submit_button(button_label)
    return submitted, {
        "length": length, "depth": depth, "height": height,
        "mat_thick": mat_thick, "inside_lam": inside_lam,
        "outside_lam": outside_lam, "plinth": plinth,
        "drawers": drawers, "drawer_h": drawer_h,
        "left_shelves": left_shelves, "right_shelves": right_shelves
    }

def calc_type3(data):
    def mm(val): return f"{round(val,1)} mm"
    groove_thick = 6.0
    T_ALL = data["mat_thick"] + data["inside_lam"] + data["outside_lam"]
    out = []

    out.append(f"Side Panels: 2 pcs — {mm(data['height'])} × {mm(data['depth'])}")
    out.append(f"Top Panel: 1 pc — {mm(data['length'] - 2*T_ALL)} × {mm(data['depth'])}")
    out.append(f"Bottom Panel: 1 pc — {mm(data['length'] - 2*T_ALL)} × {mm(data['depth'])}")
    out.append(f"Back Panel (6mm): 1 pc — {mm(data['height'] - data['plinth'] - 2*groove_thick)} × {mm(data['length'] - 2*groove_thick)}")
    out.append(f"Partition: 1 pcs — {mm(data['height']  - data['plinth'] - 2*T_ALL)} × {mm(data['depth'] - groove_thick)}")


    if data.get("left_shelves", 0) > 0:
        shelf_len = ((data["length"] - 3*T_ALL) * 2)/3
        shelf_dep = data["depth"] - T_ALL - groove_thick
        out.append(f"Left Shelves: {data['left_shelves']} pcs — {mm(shelf_len)} × {mm(shelf_dep)}")
        out.append(f"Left Shelves vertical: {data['left_shelves']} pcs — {mm(shelf_len / 3)} × {mm(shelf_dep)}")
     
    if data.get("right_shelves", 0) > 0:
        shelf_len = (data["length"] - 3*T_ALL) /3
        shelf_dep = data["depth"] - T_ALL - groove_thick
        out.append(f"Right Shelves: {data['right_shelves']} pcs — {mm(shelf_len)} × {mm(shelf_dep)}")

    door_w = (data["length"] / 3) - (2 * data["outside_lam"])
    door_h = data["height"] - data["plinth"]
    out.append(f"Doors: 3 pcs — {mm(door_h)} × {mm(door_w)}")

    if data.get("drawers", 0) > 0:
        drawer_side = data["depth"] - 3*T_ALL
        out.append(f"Drawer Sides: {data['drawers']*2} pcs — {mm(drawer_side)} × {mm(data['drawer_h'] - 2*T_ALL)}")
        out.append(f"Drawer Back: {data['drawers']} pcs — {mm(shelf_len - 5*T_ALL)} × {mm(data['drawer_h'] - 2*T_ALL)}")
        out.append(f"Drawer Front: {data['drawers']} pcs — {mm(shelf_len - 5*T_ALL) } × {mm((data['drawer_h'] - 2*T_ALL)/2)}")
        out.append(f"Drawer Bottoms - (6mm): {data['drawers']} pcs — {mm(shelf_len - 3*T_ALL)} × {mm(data['depth'] - 2*T_ALL)}")
        out.append(f"Side Extra Pieces: {data['drawers']*3} pcs — {mm(drawer_side) } × {mm(data['drawer_h'] - T_ALL)}")
        out.append(f"Front Extra Pieces: {data['drawers']} pcs — {mm(shelf_len - 1*T_ALL) } × {mm(data['drawer_h'] - T_ALL)}")
    




    
    out.append(f"Front Extra Pieces on Down: 1 pcs — {mm(data['length'] - 2*T_ALL + 2)} × {data["plinth"]}")

    return out

