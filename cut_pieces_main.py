import streamlit as st
import wardrobe_type1
import wardrobe_type2
import wardrobe_type3

# --- Map wardrobe types to their form/calc functions and image paths ---
type_fns = {
    "2-Door Cupboard": (
        wardrobe_type1.form_type1,
        wardrobe_type1.calc_type1,
        "2door.jpg"
    ),
    "3-Door Cupboard Type 1": (
        wardrobe_type2.form_type2,
        wardrobe_type2.calc_type2,
        "3door.png"
    ),
    "3-Door Cupboard Type 2": (
        wardrobe_type3.form_type3,
        wardrobe_type3.calc_type3,
        "3door_2.png"
    ),
}

st.set_page_config(page_title="Wardrobe Multi-Type Material Calculator", layout="wide")
st.title("🛠️ Multi-Type Wardrobe Calculator")

# --- Session state init ---
if "all_types_inputs" not in st.session_state:
    st.session_state["all_types_inputs"] = []
    st.session_state["all_types_labels"] = []
if "edit_index" not in st.session_state:
    st.session_state["edit_index"] = None

# --- Sidebar: Add/Edit/Manage ---
with st.sidebar:
    st.header("➕ Add New / Edit Wardrobe")

    # If editing, lock type and prefill fields
    if st.session_state["edit_index"] is not None:
        st.warning(f"✏ Editing Option {st.session_state['edit_index'] + 1}")
        type_label = st.session_state["all_types_labels"][st.session_state["edit_index"]]
        prefill = st.session_state["all_types_inputs"][st.session_state["edit_index"]]
    else:
        type_label = st.selectbox("Wardrobe Type", list(type_fns.keys()), key="sidebar_type")
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
    st.header("🗂 Manage Added Wardrobes")
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
    st.header("📋 All Materials by Wardrobe Type")
    for i, tname in enumerate(st.session_state["all_types_labels"]):
        st.subheader(f"{tname} — Option {i+1}")
        calc_fn = type_fns[tname][1]
        image_path = type_fns[tname][2]
        cols = st.columns([1, 2])
        with cols[0]:
            st.image(image_path, caption=tname, use_container_width ='always')
        with cols[1]:
            mats = calc_fn(st.session_state["all_types_inputs"][i])
            for line in mats:
                st.write("- " + line)
        st.markdown("---")
else:
    st.info("No wardrobes added yet. Use the sidebar to add one.")
