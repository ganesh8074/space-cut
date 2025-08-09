import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
from rectpack import newPacker
import io
import random

class Cutspacecut:
    def __init__(self, material_length, material_width):
        self.material_length = material_length
        self.material_width = material_width

    def fit_pieces(self, pieces):
        packer = newPacker(rotation=False)  # Set rotation=True to allow piece rotation
        # Add bins (let's allow plenty - rectpack will use as few as needed)
        for _ in range(50):
            packer.add_bin(self.material_length, self.material_width)
        # Add pieces (rectangles)
        for idx, piece in enumerate(pieces):
            packer.add_rect(piece['length'], piece['width'], idx)
        packer.pack()

        # Collect sheets and cuts
        sheets = []
        for b in packer:
            cuts = []
            for rect in b:
                cuts.append({
                    "length": rect.width,
                    "width": rect.height,
                    "x_offset": rect.x,
                    "y_offset": rect.y,
                    "original_idx": rect.rid   # tracks which input piece it was
                })
            if cuts:
                sheets.append({'cuts': cuts})
        return sheets

    def assign_piece_ids_and_colors(self, sheets, pieces):
        # Consistent color and ID for same-sized pieces
        unique = {}
        cid = 1
        color_list = []
        random.seed(42)
        for _ in range(256):
            color_list.append((random.random(), random.random(), random.random()))
        for sheet in sheets:
            for cut in sheet['cuts']:
                # Use original piece dimensions for grouping
                original_piece = pieces[cut['original_idx']]
                k = (original_piece['length'], original_piece['width'])
                if k not in unique:
                    unique[k] = {'id': cid, 'color': color_list[cid-1]}
                    cid += 1
                # Assign the group info
                cut['piece_id'] = unique[k]['id']
                cut['color'] = unique[k]['color']
                cut['length'] = original_piece['length']
                cut['width'] = original_piece['width']
        return unique

    def plot_cutting_plan_vertical(self, sheets, unique_pieces):
        fig_height = 6 * len(sheets)
        fig, axes = plt.subplots(len(sheets), 1, figsize=(12, fig_height))
        if len(sheets) == 1:
            axes = [axes]
        for idx, (ax, sheet) in enumerate(zip(axes, sheets)):
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
                    f"ID:{cut['piece_id']}\n{cut['length']}x{cut['width']}",
                    ha='center',
                    va='center',
                    fontsize=8,
                    color='black'
                )
            ax.set_xlim(0, self.material_length)
            ax.set_ylim(0, self.material_width)
            ax.set_xticks(range(0, self.material_length + 100, 100))
            ax.set_yticks(range(0, self.material_width + 100, 100))
            ax.set_title(f"Sheet {idx + 1}")
            ax.set_xlabel("Length (mm)")
            ax.set_ylabel("Width (mm)")
            ax.invert_yaxis()
            ax.set_aspect('equal', adjustable='box')
        plt.tight_layout()
        st.pyplot(fig)

    def generate_pdf(self, sheets, unique_pieces, material_length, material_width):
        pdf_buffer = io.BytesIO()
        with PdfPages(pdf_buffer) as pdf:
            for idx, sheet in enumerate(sheets):
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
                        f"ID:{cut['piece_id']}\n{cut['length']}x{cut['width']}",
                        ha='center',
                        va='center',
                        fontsize=8,
                        color='black'
                    )
                ax.set_xlim(0, material_length)
                ax.set_ylim(0, material_width)
                ax.set_xticks(range(0, material_length + 100, 100))
                ax.set_yticks(range(0, material_width + 100, 100))
                ax.set_title(f"Sheet {idx + 1}")
                ax.set_xlabel("Length (mm)")
                ax.set_ylabel("Width (mm)")
                ax.invert_yaxis()
                ax.set_aspect('equal', adjustable='box')
                plt.tight_layout()
                pdf.savefig(fig)
                plt.close(fig)
            # Legend page
            fig_legend, ax_legend = plt.subplots(figsize=(8, 4))
            legend_handles = [
                mpatches.Patch(color=info['color'], label=f"ID {info['id']}: {size[0]}x{size[1]} mm")
                for size, info in sorted(unique_pieces.items(), key=lambda x: x[1]['id'])
            ]
            ax_legend.legend(handles=legend_handles, loc='center')
            ax_legend.axis('off')
            plt.tight_layout()
            pdf.savefig(fig_legend)
            plt.close(fig_legend)
        pdf_buffer.seek(0)
        return pdf_buffer

def main():
    st.set_page_config(page_title="Cut Sheet Spacecut", layout="centered")
    st.title("🛠️ Cut Sheet Spacecut")

    # Material Inputs
    st.header("📏 Material Dimensions")
    material_length = st.number_input("Material Length (mm)", min_value=1, value=2140)
    material_width = st.number_input("Material Width (mm)", min_value=1, value=1200)

    # Pieces Input
    st.header("📦 Pieces to Cut")
    num_pieces = st.number_input("Number of Different Pieces", min_value=1, max_value=20, step=1, value=3)

    pieces = []
    for i in range(num_pieces):
        st.subheader(f"Piece {i + 1}")
        length = st.number_input(f"Length of Piece {i + 1} (mm)", min_value=1, value=1, key=f"length_{i}")
        width = st.number_input(f"Width of Piece {i + 1} (mm)", min_value=1, value=1, key=f"width_{i}")
        quantity = st.number_input(f"Quantity of Piece {i + 1}", min_value=1, value=1, key=f"quantity_{i}")
        for _ in range(quantity):
            pieces.append({'length': length, 'width': width})

    # Generate button
    submitted = st.button("Generate Cutting Plan")
    if submitted:
        st.success("✅ Cutting Plan Generated")
        spacecut = Cutspacecut(material_length, material_width)
        sheets = spacecut.fit_pieces(pieces)
        unique_pieces = spacecut.assign_piece_ids_and_colors(sheets, pieces)

        # Textual plan output
        st.subheader("🔷 Cutting Plan (Textual)")
        total_cut_area = 0
        total_material_area = 0
        sheet_count = len(sheets)
        for sheet_index, sheet in enumerate(sheets):
            st.write(f"Sheet {sheet_index + 1}:")
            for piece in sheet['cuts']:
                st.write(f"  Cut Piece ID {piece['piece_id']}: {piece['length']}mm x {piece['width']}mm at "
                         f"({piece['x_offset']}mm, {piece['y_offset']}mm)")
                total_cut_area += piece['length'] * piece['width']
            total_material_area += material_length * material_width
        waste = total_material_area - total_cut_area

        st.write(f"\nTotal Material Used: {total_cut_area} mm²")
        st.write(f"Total Waste: {waste} mm²")
        st.write(f"\nTotal Sheets Used: {sheet_count}")

        # Visualization (vertical layout)
        st.subheader("🔷 Cutting Plan (Visualization)")
        spacecut.plot_cutting_plan_vertical(sheets, unique_pieces)

        # PDF download
        pdf_bytes = spacecut.generate_pdf(sheets, unique_pieces, material_length, material_width)
        st.download_button(
            label="📥 Download Cutting Plan PDF",
            data=pdf_bytes,
            file_name="cutting_plan.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()
