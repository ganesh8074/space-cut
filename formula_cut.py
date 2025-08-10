import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import MaxNLocator
from rectpack import newPacker, MaxRectsBssf
import io
import random

st.set_page_config(page_title="SpaceCraft Cut Sheet", page_icon="✂️", layout="wide")

# ============================ UI ============================
with st.sidebar:
    st.title("✂️ Sheet Optimizer")
    st.markdown("## ⚙️Original Material Size")

    material_length = st.number_input("Material Length (mm)", min_value=1, value=2140)
    material_width  = st.number_input("Material Width (mm)",  min_value=1, value=1200)

    allow_rotation =True
    #allow_rotation = st.toggle("Allow Piece Rotation (try both orientations)", value=True)
    #st.caption("This uses your legacy greedy per-sheet logic. No kerf applied (exact part sizes).")

    st.markdown("---")
    st.markdown("## 📋 Pieces Input")
    mode = st.radio("Piece Input Mode", ["Table", "CSV Upload"], horizontal=True)

    if mode == "Table":
        example = pd.DataFrame({
            "Length (mm)": [1000, 2000, 1500, 860, 698, 917],
            "Width (mm)":  [300,  1200, 1100, 589, 175, 897],
            "Quantity":    [1,    14,   10,   5,   10,  5]
        })
        pieces_df = st.data_editor(
            example, num_rows="dynamic", use_container_width=True, hide_index=True, key="pieces_table"
        )
    else:
        up = st.file_uploader("Upload CSV (Length (mm), Width (mm), Quantity)", type=["csv"])
        pieces_df = pd.read_csv(up) if up else pd.DataFrame({"Length (mm)": [], "Width (mm)": [], "Quantity": []})

    st.markdown("---")
    dark_mode = st.toggle("🌒 Dark Mode UI", value=False)
    #show_instructions = st.checkbox("Show Instructions & Tips", value=True)
    show_instructions = False


if dark_mode:
    st.markdown("""
    <style>
      .stApp, .block-container { background:#1e1e1e; color:#ddd; }
      .stButton>button { background:#2a2a2a; color:#fff; border:1px solid #444; }
      .stDataFrame, .stDataEditor { filter: invert(0.95) hue-rotate(180deg); }
    </style>
    """, unsafe_allow_html=True)

st.title("🛠️ Cut Sheet Spacecut Pro — Legacy Greedy")

if show_instructions:
    with st.expander("ℹ️ What this mode does", expanded=True):
        st.markdown("""
- **Legacy greedy per-sheet** fitting (your working logic).  
- Sort pieces by **area (descending)**.  
- For each piece: try **Sheet 1**, then **Sheet 2**, … using `(L,W)` and `(W,L)` if rotation is enabled.  
- If it fits an existing sheet, commit; otherwise **open a new sheet**.  
- **No kerf** applied; pieces are placed at **true sizes** (exact, no shrink).  
        """)

# ============================ Legacy Greedy Core ============================
def try_pack_in_single_sheet(sheet_W, sheet_H, existing_rects, candidate_rect, algo=MaxRectsBssf):
    """
    existing_rects: list of (w, h, rid) already placed in this sheet
    candidate_rect: (w, h, rid) to test
    Returns: (fits: bool, packed_rects: list of dicts if fits else None)
    """
    packer = newPacker(rotation=False, pack_algo=algo)
    packer.add_bin(sheet_W, sheet_H)
    for (w, h, rid) in existing_rects + [candidate_rect]:
        packer.add_rect(w, h, rid=rid)
    packer.pack()
    bins = list(packer)
    if not bins:
        return False, None
    b0 = bins[0]
    if len(b0) != len(existing_rects) + 1:
        return False, None

    rects = []
    for r in b0:
        rects.append({
            "length":   r.width,   # rectpack stores (w,h); we draw length along X
            "width":    r.height,  # and width along Y
            "x_offset": r.x,
            "y_offset": r.y,
            "original_idx": r.rid
        })
    return True, rects

def greedy_fit_pieces(material_length, material_width, pieces, allow_rotation=True):
    """
    1) Sort by area desc
    2) For each piece, try to fit in each existing sheet (both orientations if allowed)
    3) If not, open a new sheet
    Returns: sheets = [{'cuts': [ {length,width,x_offset,y_offset,original_idx}, ... ]}, ...]
    """
    sheets = []
    sheet_rects = []  # [(w,h,rid), ...]

    # Sort by area (desc)
    pieces_sorted = sorted(
        [{'length': p['length'], 'width': p['width'], 'idx': i}
         for i, p in enumerate(pieces)],
        key=lambda x: x['length'] * x['width'],
        reverse=True
    )

    for p in pieces_sorted:
        L, W, rid = int(p['length']), int(p['width']), int(p['idx'])

        orientations = [(L, W)]
        if allow_rotation and (L != W):
            orientations.append((W, L))

        placed = False

        # Try to place into existing sheets
        for s_i, existing in enumerate(sheet_rects):
            for (candW, candH) in orientations:
                fits, rects = try_pack_in_single_sheet(
                    material_length, material_width,
                    existing_rects=existing,
                    candidate_rect=(candW, candH, rid)
                )
                if fits:
                    sheet_rects[s_i] = existing + [(candW, candH, rid)]
                    sheets[s_i] = {"cuts": rects}
                    placed = True
                    break
            if placed:
                break

        # If not placed, open a new sheet (first orientation that fits)
        if not placed:
            chosen = None
            for (candW, candH) in orientations:
                fits, rects = try_pack_in_single_sheet(
                    material_length, material_width,
                    existing_rects=[],
                    candidate_rect=(candW, candH, rid)
                )
                if fits:
                    chosen = (candW, candH)
                    sheets.append({"cuts": rects})
                    sheet_rects.append([chosen + (rid,)])
                    break
            if not chosen:
                # Piece larger than sheet: still place for visibility
                sheets.append({"cuts": [{
                    "length": L, "width": W, "x_offset": 0, "y_offset": 0, "original_idx": rid
                }]})
                sheet_rects.append([(L, W, rid)])

    return sheets

def assign_piece_ids_and_colors(sheets, pieces):
    """
    Stable ID/color for same TRUE size; DO NOT overwrite packed sizes.
    """
    unique = {}
    cid = 1
    rng = random.Random(42)
    palette = [(rng.random(), rng.random(), rng.random()) for _ in range(2048)]

    for sheet in sheets:
        for cut in sheet['cuts']:
            op = pieces[cut['original_idx']]
            key = (int(op['length']), int(op['width']))
            if key not in unique:
                unique[key] = {'id': cid, 'color': palette[cid-1]}
                cid += 1
            cut['piece_id'] = unique[key]['id']
            cut['color'] = unique[key]['color']
    return unique

# ============================ Plot / PDF ============================
def draw_sheet(ax, sheet, mat_L, mat_W):
    for c in sheet["cuts"]:
        ax.add_patch(mpatches.Rectangle(
            (c["x_offset"], c["y_offset"]), c["length"], c["width"],
            edgecolor="black", facecolor=c["color"], alpha=0.7
        ))
        ax.text(
            c["x_offset"] + c["length"]/2,
            c["y_offset"] + c["width"]/2,
            f"ID:{c['piece_id']}\n{int(c['length'])}×{int(c['width'])}",
            ha="center", va="center", fontsize=8, color="black"
        )
    ax.set_xlim(0, mat_L)
    ax.set_ylim(0, mat_W)
    ax.invert_yaxis()
    ax.set_aspect("equal", adjustable="box")
    ax.xaxis.set_major_locator(MaxNLocator(nbins=10, integer=True))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=10, integer=True))
    ax.set_xlabel("Length (mm)")
    ax.set_ylabel("Width (mm)")

def plot_tabs(material_length, material_width, sheets):
    st.subheader("🔷 Cutting Plan Visualization")
    tabs = st.tabs([f"Sheet {i+1}" for i in range(len(sheets))] or ["No sheets"])
    for i, (t, sh) in enumerate(zip(tabs, sheets)):
        with t:
            fig, ax = plt.subplots(figsize=(10, 7))
            draw_sheet(ax, sh, material_length, material_width)
            ax.set_title(f"Sheet {i+1}")
            st.pyplot(fig)
            plt.close(fig)

def generate_pdf(sheets, unique_pieces, material_length, material_width):
    pdf_buffer = io.BytesIO()
    with PdfPages(pdf_buffer) as pdf:
        for idx, sheet in enumerate(sheets, start=1):
            fig, ax = plt.subplots(figsize=(12, 8))
            draw_sheet(ax, sheet, material_length, material_width)
            ax.set_title(f"Sheet {idx}")
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)
        # Legend
        fig_leg, ax_leg = plt.subplots(figsize=(8, 4))
        handles = [
            mpatches.Patch(color=info["color"], label=f"ID {info['id']}: {size[0]}×{size[1]} mm")
            for size, info in sorted(unique_pieces.items(), key=lambda x: x[1]["id"])
        ]
        if handles:
            ax_leg.legend(handles=handles, loc="center")
        ax_leg.axis("off")
        plt.tight_layout()
        pdf.savefig(fig_leg)
        plt.close(fig_leg)
    pdf_buffer.seek(0)
    return pdf_buffer

# ============================ Run ============================
if st.sidebar.button("🎯 Generate Cutting Plan", use_container_width=True):
    # Expand rows by quantity
    pieces = []
    for _, r in pieces_df.iterrows():
        try:
            L = int(r["Length (mm)"]); W = int(r["Width (mm)"]); Q = int(r["Quantity"])
        except Exception:
            continue
        for _ in range(max(0, Q)):
            pieces.append({'length': L, 'width': W})

    if not pieces:
        st.warning("Please add at least one valid piece.")
        st.stop()

    sheets = greedy_fit_pieces(material_length, material_width, pieces, allow_rotation=allow_rotation)
    uniq = assign_piece_ids_and_colors(sheets, pieces)

    # Textual + metrics
    st.subheader("🔷 Cutting Plan (Textual)")
    total_cut_area = 0
    total_material_area = 0
    for i, sheet in enumerate(sheets, start=1):
        st.write(f"**Sheet {i}**")
        for c in sheet["cuts"]:
            st.write(f"ID {c['piece_id']}: {int(c['length'])}×{int(c['width'])} mm "
                     f"at ({int(c['x_offset'])}, {int(c['y_offset'])})")
            total_cut_area += c["length"] * c["width"]
        total_material_area += material_length * material_width

    waste = total_material_area - total_cut_area
    st.write(f"\nTotal Material Used: {int(total_cut_area):,} mm²")
    st.write(f"Total Waste: {int(waste):,} mm²")
    st.write(f"**Total Sheets Used: {len(sheets)}**")

    # Plots
    plot_tabs(material_length, material_width, sheets)

    # PDF
    pdf = generate_pdf(sheets, uniq, material_length, material_width)
    st.download_button("📥 Download Cutting Plan PDF", data=pdf, file_name="cutting_plan.pdf", mime="application/pdf")

else:
    st.info("Fill inputs and click **Generate Cutting Plan**.")
