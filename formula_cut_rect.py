import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
from rectpack import newPacker, MaxRectsBssf
import io
import random

# ---------------- Utility: pack test for a single sheet ----------------
def try_pack_in_single_sheet(sheet_W, sheet_H, existing_rects, candidate_rect, algo=MaxRectsBssf):
    """
    existing_rects: list of (w, h, rid) already placed in this sheet
    candidate_rect: (w, h, rid) to test
    Returns: (fits: bool, packed_rects: list of dicts if fits else None)
    We use rotation=False here and explicitly control orientation of the candidate.
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

    # Build rects in sheet coordinates from packer (respecting rotations already applied)
    rects = []
    for r in b0:
        rects.append({
            "length":   r.width,   # rectpack's (w,h); we draw length along X
            "width":    r.height,  # and width along Y
            "x_offset": r.x,
            "y_offset": r.y,
            "original_idx": r.rid
        })
    return True, rects

# ---------------- Core greedy fitter ----------------
def greedy_fit_pieces(material_length, material_width, pieces, allow_rotation=True):
    """
    pieces: list[{'length': L, 'width': W, 'idx': i}]
    Strategy:
      1) Sort by area desc
      2) For each piece:
         - Try each existing sheet in order
         - For each sheet, try orientations: [(L,W)] + [(W,L)] if allow_rotation
         - If any orientation fits that sheet, accept and update the sheet layout
         - Else start a new sheet and place it there (choosing first orientation that fits)
    Returns: sheets = [{'cuts': [ {length,width,x_offset,y_offset,original_idx}, ... ]}, ...]
    """
    # Keep a parallel structure of the raw sizes we add to each sheet for re-pack attempts
    sheets = []          # [{'cuts': ...}]
    sheet_rects = []     # [[(w,h,rid), ...], ...]

    # Sort by area (desc)
    pieces_sorted = sorted(
        [{'length': p['length'], 'width': p['width'], 'idx': i}
         for i, p in enumerate(pieces)],
        key=lambda x: x['length'] * x['width'],
        reverse=True
    )

    for p in pieces_sorted:
        L, W, rid = int(p['length']), int(p['width']), int(p['idx'])

        # Orientation candidates for this piece
        orientations = [(L, W)]
        if allow_rotation and (L != W):
            orientations.append((W, L))

        placed = False

        # Try to place into an existing sheet
        for s_i, existing in enumerate(sheet_rects):
            for (candW, candH) in orientations:
                fits, rects = try_pack_in_single_sheet(
                    material_length, material_width,
                    existing_rects=existing,
                    candidate_rect=(candW, candH, rid)
                )
                if fits:
                    # Commit this placement to the sheet
                    sheet_rects[s_i] = existing + [(candW, candH, rid)]
                    sheets[s_i] = {"cuts": rects}  # replace with the latest packed positions
                    placed = True
                    break
            if placed:
                break

        # If not placed, open a new sheet and place the first orientation that fits
        if not placed:
            chosen = None
            for (candW, candH) in orientations:
                # For a new sheet, it should fit unless piece > sheet
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
                # Piece larger than sheet: still place it at origin (it will overflow visually)
                sheets.append({"cuts": [{
                    "length": L, "width": W, "x_offset": 0, "y_offset": 0, "original_idx": rid
                }]})
                sheet_rects.append([(L, W, rid)])

    return sheets

# ---------------- Color + ID assignment (no size overwrite!) ----------------
def assign_piece_ids_and_colors(sheets, pieces):
    """
    - Stable ID/color for same TRUE size (L,W) from input 'pieces'
    - DO NOT overwrite cut['length']/'width'] to avoid rotation/overlap bugs
    """
    unique = {}
    cid = 1
    rng = random.Random(42)
    palette = [(rng.random(), rng.random(), rng.random()) for _ in range(1024)]

    for sheet in sheets:
        for cut in sheet['cuts']:
            op = pieces[cut['original_idx']]  # original (true) size for grouping
            key = (int(op['length']), int(op['width']))
            if key not in unique:
                unique[key] = {'id': cid, 'color': palette[cid-1]}
                cid += 1
            cut['piece_id'] = unique[key]['id']
            cut['color'] = unique[key]['color']
            # IMPORTANT: do not assign cut['length']=..., cut['width']=... here.
            # Leave the packed size from rectpack (respects rotation).
    return unique

# ---------------- Plotting ----------------
def plot_cutting_plan_tabs(material_length, material_width, sheets):
    st.subheader("🔷 Cutting Plan (Visualization)")
    if not sheets:
        st.info("No sheets to display.")
        return
    tabs = st.tabs([f"Sheet {i+1}" for i in range(len(sheets))])
    for i, (tab, sheet) in enumerate(zip(tabs, sheets)):
        with tab:
            fig, ax = plt.subplots(figsize=(10, 7))
            for cut in sheet['cuts']:
                ax.add_patch(
                    mpatches.Rectangle(
                        (cut['x_offset'], cut['y_offset']),
                        cut['length'], cut['width'],
                        edgecolor='black',
                        facecolor=cut['color'],
                        alpha=0.7
                    )
                )
                ax.text(
                    cut['x_offset'] + cut['length'] / 2,
                    cut['y_offset'] + cut['width'] / 2,
                    f"ID:{cut['piece_id']}\n{int(cut['length'])}x{int(cut['width'])}",
                    ha='center', va='center', fontsize=8, color='black'
                )
            # Axes EXACTLY the size of the material
            ax.set_xlim(0, material_length)
            ax.set_ylim(0, material_width)
            ax.set_title(f"Sheet {i+1}")
            ax.set_xlabel("Length (mm)")
            ax.set_ylabel("Width (mm)")
            ax.invert_yaxis()
            ax.set_aspect('equal', adjustable='box')
            st.pyplot(fig)
            plt.close(fig)

# ---------------- PDF export ----------------
def generate_pdf(sheets, unique_pieces, material_length, material_width):
    pdf_buffer = io.BytesIO()
    with PdfPages(pdf_buffer) as pdf:
        for idx, sheet in enumerate(sheets, start=1):
            fig, ax = plt.subplots(figsize=(12, 8))
            for cut in sheet['cuts']:
                ax.add_patch(
                    mpatches.Rectangle(
                        (cut['x_offset'], cut['y_offset']),
                        cut['length'], cut['width'],
                        edgecolor='black',
                        facecolor=cut['color'],
                        alpha=0.7
                    )
                )
                ax.text(
                    cut['x_offset'] + cut['length'] / 2,
                    cut['y_offset'] + cut['width'] / 2,
                    f"ID:{cut['piece_id']}\n{int(cut['length'])}x{int(cut['width'])}",
                    ha='center', va='center', fontsize=8, color='black'
                )
            ax.set_xlim(0, material_length)
            ax.set_ylim(0, material_width)
            ax.set_title(f"Sheet {idx}")
            ax.set_xlabel("Length (mm)")
            ax.set_ylabel("Width (mm)")
            ax.invert_yaxis()
            ax.set_aspect('equal', adjustable='box')
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)
        # Legend page (IDs are grouped by TRUE size)
        fig_legend, ax_legend = plt.subplots(figsize=(8, 4))
        legend_handles = [
            mpatches.Patch(color=info['color'], label=f"ID {info['id']}: {size[0]}x{size[1]} mm")
            for size, info in sorted(unique_pieces.items(), key=lambda x: x[1]['id'])
        ]
        if legend_handles:
            ax_legend.legend(handles=legend_handles, loc='center')
        ax_legend.axis('off')
        plt.tight_layout()
        pdf.savefig(fig_legend)
        plt.close(fig_legend)
    pdf_buffer.seek(0)
    return pdf_buffer

# ---------------- Streamlit App ----------------
def main():
    st.set_page_config(page_title="Cut Sheet Spacecut", layout="centered")
    st.title("🛠️ Cut Sheet Spacecut (Greedy per-sheet, rotation-aware)")

    # Material Inputs
    st.header("📏 Material Dimensions")
    material_length = st.number_input("Material Length (mm)", min_value=1, value=2140)
    material_width  = st.number_input("Material Width (mm)",  min_value=1, value=1200)

    # Rotation toggle (your earlier class had rotation=True hardcoded)
    allow_rotation = st.toggle("Allow Piece Rotation (try both orientations)", value=True)

    # Pieces Input
    st.header("📦 Pieces to Cut")
    num_pieces = st.number_input("Number of Different Pieces", min_value=1, max_value=200, step=1, value=3)

    pieces = []
    for i in range(num_pieces):
        st.subheader(f"Piece {i + 1}")
        length = st.number_input(f"Length of Piece {i + 1} (mm)", min_value=1, value=1, key=f"length_{i}")
        width  = st.number_input(f"Width of Piece {i + 1} (mm)",  min_value=1, value=1, key=f"width_{i}")
        quantity = st.number_input(f"Quantity of Piece {i + 1}", min_value=1, value=1, key=f"quantity_{i}")
        for _ in range(quantity):
            pieces.append({'length': length, 'width': width})

    # Generate button
    submitted = st.button("Generate Cutting Plan")
    if submitted:
        st.success("✅ Cutting Plan Generated")

        # Fit with greedy per-sheet strategy trying both orientations per piece
        sheets = greedy_fit_pieces(material_length, material_width, pieces, allow_rotation=allow_rotation)

        # Assign consistent IDs/colors by TRUE size (no size overwrite)
        unique_pieces = assign_piece_ids_and_colors(sheets, pieces)

        # Textual plan output + metrics
        st.subheader("🔷 Cutting Plan (Textual)")
        total_cut_area = 0
        total_material_area = 0
        for sheet_index, sheet in enumerate(sheets, start=1):
            st.write(f"Sheet {sheet_index}:")
            for cut in sheet['cuts']:
                st.write(
                    f"  Cut Piece ID {cut['piece_id']}: {int(cut['length'])}mm x {int(cut['width'])}mm at "
                    f"({int(cut['x_offset'])}mm, {int(cut['y_offset'])}mm)"
                )
                total_cut_area += cut['length'] * cut['width']
            total_material_area += material_length * material_width

        waste = total_material_area - total_cut_area
        st.write(f"\nTotal Material Used: {int(total_cut_area)} mm²")
        st.write(f"Total Waste: {int(waste)} mm²")
        st.write(f"\nTotal Sheets Used: {len(sheets)}")

        # Visualization (tabs, axes exactly sheet size)
        plot_cutting_plan_tabs(material_length, material_width, sheets)

        # PDF download
        pdf_bytes = generate_pdf(sheets, unique_pieces, material_length, material_width)
        st.download_button(
            label="📥 Download Cutting Plan PDF",
            data=pdf_bytes,
            file_name="cutting_plan.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()
