import streamlit as st

def form_type_tv(prefill=None, button_label="Add"):
    if prefill is None:
        prefill = {}

    tv_height = st.number_input("Total TV Unit Height (mm)", min_value=1000, value=prefill.get("height", 2515), step=5, key="tv_h")
    tv_width = st.number_input("Total TV Unit Width (mm)", min_value=1000, value=prefill.get("width", 3830), step=5, key="tv_w")
    rft_height = st.number_input("Rafter Height (mm)", min_value=100, value=prefill.get("height", 2515), step=5, key="rf_h")
    rft_width = st.number_input("Rafter Width (mm)", min_value=100, value=prefill.get("width", 905), step=5, key="rf_w")
    rlam_height = st.number_input("Rafter Laminate Height (mm)", min_value=100, value=prefill.get("height", 2215), step=5, key="rl_h")
    rlam_width = st.number_input("Rafter Laminate Width (mm)", min_value=100, value=prefill.get("width", 605), step=5, key="rl_w")
    ros_height = st.number_input("Right Open Shelf Height (mm)", min_value=100, value=prefill.get("height", 2290), step=5, key="ros_h")
    ros_width = st.number_input("Right Open Shelf Width (mm)", min_value=100, value=prefill.get("width", 575), step=5, key="ros_w")
    ros_depth = st.number_input("Right Open Shelf Depth (mm)", min_value=100, value=prefill.get("depth", 400), step=5, key="rps_d")
    num_selfs = st.number_input("Number of Right Shelfs", min_value=0, max_value=10, value=prefill.get("num_drawers", 4), step=1, key="n_sh")
    num_drawers = st.number_input("Number of Drawers", min_value=0, max_value=10, value=prefill.get("num_drawers", 4), step=1, key="tv_drawers")
    draw_height = st.number_input("Drawer Height (mm)", min_value=50, value=prefill.get("drawer_h", 225), step=5, key="tv_drawer_h")
    #draw_width = st.number_input("Drawer Width (mm)", min_value=50, value=prefill.get("drawer_w", 731), step=5, key="tv_drawer_w")
    #ros_depth = st.number_input("Drawer Depth (mm)", min_value=50, value=prefill.get("drawer_d", 400), step=5, key="tv_drawer_d")
    bos_height = st.number_input("Bottom Open Shelf Height (mm)", min_value=100, value=prefill.get("bos_height", 150), step=5, key="tv_bos_h")
    blam_height = st.number_input("Barley Laminate Height (mm)", min_value=100, value=prefill.get("height", 1911), step=5, key="bl_h")
    blam_width = st.number_input("Barley Laminate Width (mm)", min_value=100, value=prefill.get("width", 600), step=5, key="bl_w")
    submitted = st.form_submit_button(button_label)
    
    inputs = {
        "tv_height": tv_height,
        "tv_width": tv_width,
        "rft_height": rft_height,
        "rft_width": rft_width,
        "rlam_height": rlam_height,
        "rlam_width": rlam_width,
        "ros_height": ros_height,
        "ros_width": ros_width,
        "ros_depth": ros_depth,
        "num_selfs": num_selfs,
        "num_drawers": num_drawers,
        "draw_height": draw_height,
        "bos_height": bos_height,
        "blam_height": blam_height,
        "blam_width": blam_width
    }
    return submitted, inputs

def calc_type_tv(data):
    lines = []

    # Material 1 – Rafters
    lines.append("Material 1 – Rafters")
    lines.append(f"• 1 pc — {int(data["rft_height"])}× {int(data["rft_width"])} - {int(data["rlam_height"]) - 2}× {int(data["rlam_width"]) - 2}")
    lines.append(f"• Multiple Rafter Pieces — {int(data["tv_height"] - data["draw_height"] - data["bos_height"] - data["blam_height"])}× {int(data["tv_width"] - data["rft_width"] - data["ros_width"])}")


    # Material 2 – Main Panels
    lines.append("Material 2 – White Barley")
    lines.append(f"• 1 pc — {int(data["blam_height"])}× {int(data["tv_width"]) - int(data["rft_width"])- int(data["blam_width"]) -int(data["ros_width"]) + 4}")
    lines.append(f"• Drawer Doors {int(data["num_drawers"])} pcs : {int(data["draw_height"]- 20)}×{int(int((data["tv_width"] - data["rft_width"]))/int(data["num_drawers"]))}")


    # Material 3 – Overlays
    lines.append("Material 3 – Wooden Laminate")

    lines.append(f"• Rafter Laminate 1 pc — {int(data["rlam_height"])}× {int(data["rlam_width"])}")
    lines.append(f"• Barley Laminate 1 pc — {int(data["blam_height"])}× {int(data["blam_width"])}")
    lines.append(f"• Right Open shelf Side 2 pc — {int(data["ros_height"])}× {int(data["ros_depth"])}")
    lines.append(f"• Right Open shelf Back 1 pc — {int(data["ros_height"])}× {int(data["ros_width"])}")
    lines.append(f"• Right Open shelf middle {int(data["num_selfs"])} pcs — {int(data["ros_width"] - 2 * 18)}× {int(data["ros_depth"] - 18)}")
    lines.append(f"• Bottom Open Shelf Top 1 pc : {int(data["tv_width"] - data["rft_width"] - data["ros_width"] - 2)}×{int(data["ros_depth"]) - 1}")
    lines.append(f"• Bottom Open Shelf side 2 pcs : {int(data["bos_height"]- 40)}×{int(data["ros_depth"]) - 1}")
    lines.append(f"• Drawer Open Shelf Mid & Botom 2 pcs : {int(data["tv_width"] - data["rft_width"] - 2)}×{int(data["ros_depth"]) - 1}")
    lines.append(f"• Drawer Shelf side {int(data["num_drawers"] + 1)} pcs : {int(data["draw_height"]- 40)}×{int(data["ros_depth"]) - 1}")
    lines.append(f"• Drawer Side {int(data["num_drawers"]) * 2} pcs : {int(data["draw_height"]- 50)}×{int(data["ros_depth"])}")
    lines.append(f"• Drawer Back {int(data["num_drawers"])} pcs : {int(data["draw_height"]- 50)}×{int((data["tv_width"] - data["rft_width"]))/int(data["num_drawers"]) - 5 * 18}")
    lines.append(f"• Drawer Bottom {int(data["num_drawers"])} pcs : {int(data["ros_depth"]- 20)}×{int((data["tv_width"] - data["rft_width"]))/int(data["num_drawers"]) - 5 * 18}")

  



    return lines
