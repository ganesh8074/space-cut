import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
import io
import random

class Cutspacecut:
    def __init__(self, material_length, material_width):
        self.material_length = material_length
        self.material_width = material_width
        self.material_area = material_length * material_width

    def fit_pieces(self, pieces):
        # Sort largest pieces first
        pieces = sorted(pieces, key=lambda x: x['length'] * x['width'], reverse=True)
        cutting_plan = []
        remaining_pieces = pieces[:]
        sheet_number = 0

        while remaining_pieces:
            sheet_number += 1
            sheet = {
                'length': self.material_length,
                'width': self.material_width,
                'cuts': [],
                'remaining': [(0, 0, self.material_length, self.material_width)]
            }

            while True:
                placed_in_this_pass = False
                for piece in remaining_pieces[:]:
                    for idx, (x_offset, y_offset, rem_length, rem_width) in enumerate(sheet['remaining']):
                        if piece['length'] <= rem_length and piece['width'] <= rem_width:
                            # Place cut
                            sheet['cuts'].append({
                                'length': piece['length'],
                                'width': piece['width'],
                                'x_offset': x_offset,
                                'y_offset': y_offset
                            })
                            remaining_pieces.remove(piece)

                            # Calculate leftover free spaces
                            new_spaces = []
                            if piece['length'] < rem_length:
                                new_spaces.append((x_offset + piece['length'], y_offset, rem_length - piece['length'], rem_width))
                            if piece['width'] < rem_width:
                                new_spaces.append((x_offset, y_offset + piece['width'], rem_length, rem_width - piece['width']))

                            # Update spaces
                            del sheet['remaining'][idx]
                            sheet['remaining'].extend(new_spaces)

                            placed_in_this_pass = True
                            break
                    if placed_in_this_pass:
                        break
                if not placed_in_this_pass:
                    break

            cutting_plan.append(sheet)
        return cutting_plan

    def assign_piece_ids_and_colors(self, sheets):
        # Assign a unique ID and consistent color for each unique piece size across sheets
        unique_pieces = {}
        piece_id = 1
        colors = []

        # Generate a list of distinct colors
        random.seed(42)  # Fix seed for reproducibility
        for _ in range(100):  # 100 distinct colors max (modify if needed)
            colors.append((random.random(), random.random(), random.random()))

        for sheet in sheets:
            for cut in sheet['cuts']:
                key = (cut['length'], cut['width'])
                if key not in unique_pieces:
                    unique_pieces[key] = {'id': piece_id, 'color': colors[piece_id - 1]}
                    piece_id += 1
                cut['piece_id'] = unique_pieces[key]['id']
                cut['color'] = unique_pieces[key]['color']

        return unique_pieces

    def plot_cutting_plan_vertical(self, sheets, unique_pieces):
        # Create vertical plots - one below another
        fig_height = 6 * len(sheets)
        fig, axes = plt.subplots(len(sheets), 1, figsize=(12, fig_height))
        if len(sheets) == 1:
            axes = [axes]

        for sheet_index, (ax, sheet) in enumerate(zip(axes, sheets)):
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
            ax.set_title(f"Sheet {sheet_index + 1}")
            ax.set_xlabel("Length (mm)")
            ax.set_ylabel("Width (mm)")
            ax.invert_yaxis()
            ax.set_aspect('equal', adjustable='box')

        plt.tight_layout()
        st.pyplot(fig)

    def generate_pdf(self, sheets, unique_pieces, material_length, material_width):
        pdf_buffer = io.BytesIO()
        with PdfPages(pdf_buffer) as pdf:
            for sheet_index, sheet in enumerate(sheets):
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
                ax.set_title(f"Sheet {sheet_index + 1}")
                ax.set_xlabel("Length (mm)")
                ax.set_ylabel("Width (mm)")
                ax.invert_yaxis()
                ax.set_aspect('equal', adjustable='box')
                plt.tight_layout()

                pdf.savefig(fig)
                plt.close(fig)

            # Add a legend page
            fig_legend, ax_legend = plt.subplots(figsize=(8, 4))
            legend_handles = []
            labels = []
            for size, info in sorted(unique_pieces.items(), key=lambda x: x[1]['id']):
                patch = mpatches.Patch(color=info['color'], label=f"ID {info['id']}: {size[0]}x{size[1]} mm")
                legend_handles.append(patch)
                labels.append(f"ID {info['id']}: {size[0]}x{size[1]} mm")

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

        unique_pieces = spacecut.assign_piece_ids_and_colors(sheets)

        # Textual plan output
        st.subheader("🔷 Cutting Plan (Textual)")
        total_cut_area = 0
        total_material_area = 0
        sheet_count = len(sheets)

        for sheet_index, sheet in enumerate(sheets):
            st.write(f"Sheet {sheet_index + 1}:")
            for piece in sheet['cuts']:
                st.write(f"  Cut Piece ID {piece['piece_id']}: {piece['length']}mm x {piece['width']}mm at ({piece['x_offset']}mm, {piece['y_offset']}mm)")
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
