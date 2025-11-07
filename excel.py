# merge_app.py
import streamlit as st
import pandas as pd
from io import BytesIO
from pathlib import Path

st.set_page_config(page_title="Merge CSV/XLSX → One Excel", layout="wide")

st.title("Merge multiple CSV / XLSX files into one Excel workbook")
st.write("Upload files (CSV or XLSX). Each input file or each sheet inside an XLSX becomes a separate worksheet in the output workbook.")

uploaded = st.file_uploader("Choose CSV/XLSX files", type=["csv", "xlsx", "xls"], accept_multiple_files=True)

def read_uploaded(file):
    """Return list of tuples (sheet_hint, dataframe)."""
    name = Path(file.name).stem
    suffix = Path(file.name).suffix.lower()
    try:
        if suffix == ".csv":
            df = pd.read_csv(file)
            return [(name, df)]
        else:
            # read_excel accepts a file-like object if using engine openpyxl
            sheets = pd.read_excel(file, sheet_name=None)
            return [(f"{name}__{sname}", df) for sname, df in sheets.items()]
    except Exception as e:
        st.error(f"Failed to read {file.name}: {e}")
        return []

def clean_sheet_name(name: str, max_len: int = 31) -> str:
    import re
    name = re.sub(r'[:\\\\\\/\\?\\*\\[\\]]', '', name)
    name = name.replace("\n"," ").replace("\r"," ").strip()
    if not name:
        name = "Sheet"
    if len(name) > max_len:
        name = name[:max_len]
    return name

def make_unique(name, used):
    if name not in used:
        used.add(name)
        return name
    i = 1
    while True:
        cand = f"{name}_{i}"
        if cand not in used:
            used.add(cand)
            return cand
        i += 1

if uploaded:
    all_sheets = []  # list of (sheet_name_hint, df, source_filename)
    for f in uploaded:
        sheets = read_uploaded(f)
        for hint, df in sheets:
            all_sheets.append((hint, df, f.name))

    st.subheader("Preview uploaded files / sheets")
    for hint, df, src in all_sheets:
        with st.expander(f"{src} → {hint} (rows: {len(df)})", expanded=False):
            st.dataframe(df.head(100))

    # Merge options
    st.sidebar.header("Merge options")
    include_index = st.sidebar.checkbox("Include DataFrame index as column", value=False)
    output_filename = st.sidebar.text_input("Output filename", value="merged.xlsx")
    if not output_filename.lower().endswith(".xlsx"):
        output_filename += ".xlsx"

    if st.sidebar.button("Create merged workbook"):
        # build workbook in-memory
        used = set()
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            for hint, df, src in all_sheets:
                cleaned = clean_sheet_name(hint)
                unique = make_unique(cleaned, used)
                try:
                    df.to_excel(writer, sheet_name=unique, index=include_index)
                except Exception as e:
                    st.error(f"Failed to write sheet {unique}: {e}")
        buffer.seek(0)
        st.success(f"Merged {len(all_sheets)} sheets. Download below.")
        st.download_button("Download merged Excel", data=buffer, file_name=output_filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

else:
    st.info("Upload one or more CSV/XLSX files to get started. Use the sample files I provided to test.")