import streamlit as st
import wardrobe_2door
import wardrobe_1door
import loft
import tv_unit_type1
import wardrobe_2door_slide
import KT_cabinet
import KT_bottle_po
import KT_blind_cp
import KT_3_tan
import KT_sink
import KT_wall_unit

# --- Map wardrobe types to their form/calc functions and image paths ---
# image_paths can be 1 or 2 paths; both will be shown one below the other.
type_fns = {
    "2-Door Normal": (
        wardrobe_2door.form_type1,
        wardrobe_2door.calc_type1,
        ["2door.jpg"]  # <— add second image if available
    ),
    "2-Door Sliding": (
        wardrobe_2door_slide.form_type1,
        wardrobe_2door_slide.calc_type1,
        ["2door_slide.png", "2door_slide_2.png"]
    ),
    "1-Door Wardrobe": (
        wardrobe_1door.form_type1,
        wardrobe_1door.calc_type1,
        ["1door.PNG", "1door_2.PNG"]  # single image is fine
    ),
    "Wardrobe Loft ": (
        loft.form_type1,
        loft.calc_type1,
        ["loft1.png", "loft2.png"]
    ),
    "TV Unit Type 1": (
        tv_unit_type1.form_type1,
        tv_unit_type1.calc_type1,
        ["tvunit1.PNG", "tvunit2.PNG"]
    ),
    "Kitchen - Cabinet": (
        KT_cabinet.form_type1,
        KT_cabinet.calc_type1,
        ["kt1.PNG", "kt2.PNG"]
    ),
     "Kitchen - BPO": (
        KT_bottle_po.form_type1,
        KT_bottle_po.calc_type1,
        ["kt1.PNG", "kt2.PNG"]
    ),
    "Kitchen - 3 Tandems": (
        KT_3_tan.form_type1,
        KT_3_tan.calc_type1,
        ["kt1.PNG", "kt2.PNG"]
    ),
    "Kitchen - Blind Corner": (
        KT_blind_cp.form_type1,
        KT_blind_cp.calc_type1,
        ["kt1.PNG", "kt2.PNG"]
    ),
    "Kitchen - Sink": (
        KT_sink.form_type1,
        KT_sink.calc_type1,
        ["kt1.PNG", "kt2.PNG"]
    ),
    "Kitchen - Wall Unit": (
        KT_wall_unit.form_type1,
        KT_wall_unit.calc_type1,
        ["kt1.PNG", "kt2.PNG"]
    ),
}

st.set_page_config(page_title=" Multi-Type Material Calculator", layout="wide")
st.title("🛠️ Multi-Type Cut Piece Calculator")

# --- Session state init ---
if "all_types_inputs" not in st.session_state:
    st.session_state["all_types_inputs"] = []
    st.session_state["all_types_labels"] = []
if "edit_index" not in st.session_state:
    st.session_state["edit_index"] = None

# --- Sidebar: Add/Edit/Manage ---
with st.sidebar:
    st.header("➕ Add New / Edit")

    # If editing, lock type and prefill fields
    if st.session_state["edit_index"] is not None:
        st.warning(f"✏ Editing Option {st.session_state['edit_index'] + 1}")
        type_label = st.session_state["all_types_labels"][st.session_state["edit_index"]]
        prefill = st.session_state["all_types_inputs"][st.session_state["edit_index"]]
    else:
        type_label = st.selectbox("Module Type", list(type_fns.keys()), key="sidebar_type")
        prefill = {}

    form_fn, _, _ = type_fns[type_label]

    with st.form("type_form"):
        button_label = "Update" if st.session_state["edit_index"] is not None else "Add"
        submitted, input_data = form_fn(prefill, button_label)
        if submitted:
            if st.session_state["edit_index"] is None:
                # Add new entry
                st.session_state["all_types_inputs"].append(input_data)
                st.session_state["all_types_labels"].append(type_label)
                st.success(f"✅ Added {type_label}")
            else:
                # Update existing
                idx = st.session_state["edit_index"]
                st.session_state["all_types_inputs"][idx] = input_data
                st.session_state["all_types_labels"][idx] = type_label
                st.session_state["edit_index"] = None
                st.success(f"✏️ Updated {type_label}")

    st.markdown("---")
    st.header("🗂 Manage Added Modules")
    for i, tname in enumerate(st.session_state["all_types_labels"]):
        st.write(f"{i+1}. {tname}")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✏ Edit", key=f"edit_{i}"):
                st.session_state["edit_index"] = i
                st.rerun()
        with col2:
            if st.button("📄 Duplicate", key=f"dup_{i}"):
                st.session_state["all_types_inputs"].append(
                    st.session_state["all_types_inputs"][i].copy()
                )
                st.session_state["all_types_labels"].append(tname)
        with col3:
            if st.button("🗑 Delete", key=f"del_{i}"):
                st.session_state["all_types_inputs"].pop(i)
                st.session_state["all_types_labels"].pop(i)
                if st.session_state["edit_index"] == i:
                    st.session_state["edit_index"] = None
                st.rerun()

# --- Main area: Outputs ---
if st.session_state["all_types_inputs"]:
    st.header("📋 All Materials by Module Type in mm")
    for i, tname in enumerate(st.session_state["all_types_labels"]):
        st.subheader(f"{tname} — Option {i+1}")
        calc_fn = type_fns[tname][1]
        image_paths = type_fns[tname][2]

        cols = st.columns([1, 2])
        with cols[0]:
            # Always treat as a list; show one below the other
            if isinstance(image_paths, str):
                image_paths = [image_paths]
            for p in image_paths:
                st.image(p, caption=tname, use_container_width=True)

        with cols[1]:
            mats = calc_fn(st.session_state["all_types_inputs"][i])
            for line in mats:
                st.write("- " + line)

            # Add download button for 2-Door Sliding
            if tname == "2-Door Sliding":
                if hasattr(wardrobe_2door_slide, "get_cutlist_df"):
                    df = wardrobe_2door_slide.get_cutlist_df(st.session_state["all_types_inputs"][i])
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Cutlist as CSV", csv,
                                       "wardrobe_2door_sliding_cutlist.csv", "text/csv")
            elif tname == "1-Door Wardrobe":
                if hasattr(wardrobe_1door, "get_cutlist_df"):
                    df = wardrobe_1door.get_cutlist_df(st.session_state["all_types_inputs"][i])
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Cutlist as CSV", csv,
                                       "wardrobe_1door_cutlist.csv", "text/csv")
            elif tname == "Wardrobe Loft ":
                if hasattr(loft, "get_cutlist_df"):
                    df = loft.get_cutlist_df(st.session_state["all_types_inputs"][i])
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Cutlist as CSV", csv,
                                       "wardrobe_loft_cutlist.csv", "text/csv")
            elif tname == "TV Unit Type 1":
                if hasattr(tv_unit_type1, "get_cutlist_df"):
                    df = tv_unit_type1.get_cutlist_df(st.session_state["all_types_inputs"][i])
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Cutlist as CSV", csv,
                                       "tv_unit_type1_cutlist.csv", "text/csv")
            elif tname == "Kitchen - Cabinet":
                if hasattr(KT_cabinet, "get_cutlist_df"):
                    df = KT_cabinet.get_cutlist_df(st.session_state["all_types_inputs"][i])
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Cutlist as CSV", csv,
                                       "kitchen_cabinet_cutlist.csv", "text/csv")
            elif tname == "Kitchen - BPO":
                if hasattr(KT_bottle_po, "get_cutlist_df"):
                    df = KT_bottle_po.get_cutlist_df(st.session_state["all_types_inputs"][i])
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Cutlist as CSV", csv,
                                       "kitchen_bpo_cutlist.csv", "text/csv")
            elif tname == "Kitchen - 3 Tandems":
                if hasattr(KT_3_tan, "get_cutlist_df"):
                    df = KT_3_tan.get_cutlist_df(st.session_state["all_types_inputs"][i])
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Cutlist as CSV", csv,
                                       "kitchen_3_tandems_cutlist.csv", "text/csv")
            elif tname == "Kitchen - Blind Corner":
                if hasattr(KT_blind_cp, "get_cutlist_df"):
                    df = KT_blind_cp.get_cutlist_df(st.session_state["all_types_inputs"][i])
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Cutlist as CSV", csv,
                                       "kitchen_blind_corner_cutlist.csv", "text/csv")
            elif tname == "Kitchen - Sink":
                if hasattr(KT_sink, "get_cutlist_df"):
                    df = KT_sink.get_cutlist_df(st.session_state["all_types_inputs"][i])
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Cutlist as CSV", csv,
                                       "kitchen_sink_cutlist.csv", "text/csv")
            elif tname == "Kitchen - Wall Unit":
                if hasattr(KT_wall_unit, "get_cutlist_df"):
                    df = KT_wall_unit.get_cutlist_df(st.session_state["all_types_inputs"][i])
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button("Download Cutlist as CSV", csv,
                                       "kitchen_wall_unit_cutlist.csv", "text/csv")

        st.markdown("---")
else:
    st.info("No Modules added yet. Use the sidebar to add one.")
