import re
import streamlit as st
import pandas as pd

import wardrobe_2door
import wardrobe_1door
import loft
import wardrobe_2door_slide
import wardrobe_3door_slide

# --- Map wardrobe types to their form/calc functions and image paths ---
# image_paths can be 1 or 2 paths; both will be shown one below the other.
type_fns = {
    "1-Door Wardrobe": (
        wardrobe_1door.form_type1,
        wardrobe_1door.calc_type1,
        ["1door.PNG", "1door_2.PNG"]  # single image is fine
    ),
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
    "3-Door Sliding": (
        wardrobe_3door_slide.form_type1,
        wardrobe_3door_slide.calc_type1,
        ["2door_slide.png", "2door_slide_2.png"]
    ),
    "Wardrobe Loft ": (
        loft.form_type1,
        loft.calc_type1,
        ["loft1.png", "loft2.png"]
    ),

}

# ---------- Helpers: normalize DF -> new columns ----------
SIX_COLS = [
    "Cut piece name",
    "Wood",
    "Colour laminate",
    "Laminate Color",
    "Short side 1",
    "Short side 2",
    "Long side 1",
    "Long side 2",
    "Groove",
]

def _dims(h, w):
    # compact dimension string (mm implied)
    try:
        return f"{round(float(h),1)} × {round(float(w),1)}"
    except Exception:
        return ""

def normalize_to_six(df):
    """
    Accepts a module DataFrame and returns a DataFrame with the six standard columns.
    Handles two cases:
      1) DF already has the six columns -> return as-is (reordered).
      2) DF has the old shape (item/qty/height_mm/width_mm[/notes]) -> map to six.
         In this case, Colour/White laminate left blank, edge biddings = 0.0.
    """
    import pandas as pd

    # Case 1: already in six-column shape
    if set([c.lower() for c in df.columns]).issuperset(
        [c.lower() for c in SIX_COLS]
    ):
        # reorder and return
        return df[[c for c in SIX_COLS if c in df.columns]]

    # Case 2: older schema -> map
    lower = {c.lower(): c for c in df.columns}
    needed = all(k in lower for k in ["item", "height_mm", "width_mm"])
    if needed:
        item_col = lower["item"]
        h_col = lower["height_mm"]
        w_col = lower["width_mm"]

        out_rows = []
        for _, r in df.iterrows():
            out_rows.append({
                "Cut piece name": r[item_col],
                "Wood": _dims(r[h_col], r[w_col]),
                "Colour laminate": "",
                "Laminate Color": "",
                "Short side 1": "",
                "Short side 2": "",
                "Long side 1": "",
                "Long side 2": "",
                "Groove": "",
            })
        return pd.DataFrame(out_rows, columns=SIX_COLS)

    # Fallback: return empty six-col DF (caller can decide to show legacy view)
    return df

def safe_filename(name: str) -> str:
    # turn "Kitchen - Cabinet" into "kitchen_cabinet"
    base = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()
    return base or "cutlist"

# ----------------------------------------------------------

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
        form_fn, calc_fn, image_paths = type_fns[tname]

        # Only show cutpiece output (images removed as requested)
        cols = st.columns([1])
        with cols[0]:
            # Try to get a DataFrame from the module
            df = None
            module_obj = {
                "1-Door Wardrobe": wardrobe_1door,
                "2-Door Normal": wardrobe_2door,
                "2-Door Sliding": wardrobe_2door_slide,
                "3-Door Sliding": wardrobe_3door_slide,
                "Wardrobe Loft ": loft,
            }[tname]

            if hasattr(module_obj, "get_cutlist_df"):
                try:
                    raw_df = module_obj.get_cutlist_df(st.session_state["all_types_inputs"][i])
                except Exception as e:
                    raw_df = None
                    st.error(f"Error generating table: {e}")

                if raw_df is not None:
                    df = normalize_to_six(raw_df)

            # Display user input log (key-value) above cutpiece table for all types
            user_inputs = st.session_state["all_types_inputs"][i]
            st.markdown("**User Inputs:**")
            keys = list(user_inputs.keys())
            values = list(user_inputs.values())
            n = len(keys)
            cols = st.columns(4)
            for idx in range(n):
                col = cols[idx % 4]
                col.write(f"**{keys[idx]}**: {values[idx]}")

            if df is not None and not df.empty and set([c.lower() for c in SIX_COLS]).issubset([c.lower() for c in df.columns]):
                # Ensure required columns exist (create if missing)
                for col in ["Short side 1", "Short side 2", "Long side 1", "Long side 2", "Groove"]:
                    if col not in df.columns:
                        df[col] = ""

                # Ensure proper column order (preserve only our standard columns)
                df = df[[c for c in SIX_COLS if c in df.columns]]

                # Derive edge bidding columns (all text) from Laminate Color
                if "Laminate Color" in df.columns:
                    col_str = df["Laminate Color"].astype(str)
                    mask_fb_bsl = col_str.str.contains("FB BSL", na=False)

                    # If FB BSL → only Long side 1 = "0.8 FB", others blank
                    if "Long side 1" in df.columns:
                        df.loc[mask_fb_bsl, "Long side 1"] = "0.8 FB"
                    for col in ["Short side 1", "Short side 2", "Long side 2"]:
                        if col in df.columns:
                            df.loc[mask_fb_bsl, col] = ""

                    # Else → Long side 1 = "Colour Bidding", others blank
                    if "Short side 1" in df.columns:
                        df.loc[~mask_fb_bsl, "Short side 1"] = ""
                    if "Short side 2" in df.columns:
                        df.loc[~mask_fb_bsl, "Short side 2"] = ""
                    if "Long side 2" in df.columns:
                        df.loc[~mask_fb_bsl, "Long side 2"] = ""
                    if "Long side 1" in df.columns:
                        df.loc[~mask_fb_bsl, "Long side 1"] = "Colour Bidding"

                # Ensure text dtypes for these derived columns
                for text_col in ["Short side 1", "Short side 2", "Long side 1", "Long side 2", "Groove"]:
                    if text_col in df.columns:
                        df[text_col] = df[text_col].where(df[text_col].notna(), "").astype(str)

                # Display editable table
                st.subheader("📊 Editable Cut List")
                st.info("💡 Click any cell to edit. Add/delete rows as needed. All changes will be saved in the CSV download.")
                
                # Display editable dataframe 
                edited_df = st.data_editor(
                    df,
                    use_container_width=True,
                    num_rows="dynamic",
                    column_config={
                        "Cut piece name": st.column_config.TextColumn("Cut piece name", width="medium"),
                        "Wood": st.column_config.TextColumn("Wood", width="medium"),
                        "Colour laminate": st.column_config.TextColumn("Colour laminate", width="medium"),
                        "Laminate Color": st.column_config.TextColumn("Laminate Color", width="medium"),
                        # All four edge bidding columns are text, derived from Colour laminate
                        "Short side 1": st.column_config.TextColumn("Short side 1", width="small"),
                        "Short side 2": st.column_config.TextColumn("Short side 2", width="small"),
                        "Long side 1": st.column_config.TextColumn("Long side 1", width="small"),
                        "Long side 2": st.column_config.TextColumn("Long side 2", width="small"),
                        "Groove": st.column_config.TextColumn("Groove", width="medium"),
                    },
                    key=f"data_editor_{i}",
                )

                # CSV download with edited data - add unique key to avoid duplicate error
                csv = edited_df.to_csv(index=False).encode('utf-8')
                fname = f"{safe_filename(tname)}_cutlist.csv"
                st.download_button("📥 Download Edited Cut List as CSV", csv, fname, "text/csv", key=f"download_{i}")
            else:
                # Fallback to legacy bullets
                mats = module_obj.calc_type1(st.session_state["all_types_inputs"][i])
                for line in mats:
                    st.write(line)

        st.markdown("---")
else:
    st.info("No Modules added yet. Use the sidebar to add one.")
