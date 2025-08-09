import streamlit as st
import matplotlib.pyplot as plt

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

            st.write(f"\n--- Starting Sheet {sheet_number} ---")
            st.write("Remaining pieces to cut (count):", len(remaining_pieces))
            #st.write("Remaining pieces list:", remaining_pieces)
            #st.write("Initial sheet remaining spaces:", sheet['remaining'])

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

                            st.write(f"\n✂️ Cut piece: {piece} at ({x_offset}, {y_offset}) in Sheet {sheet_number}")

                            # Update spaces
                            del sheet['remaining'][idx]
                            sheet['remaining'].extend(new_spaces)

                            # Debug snapshots
                            # st.write("Updated sheet cuts:", sheet['cuts'])
                            # st.write("Updated sheet remaining spaces:", sheet['remaining'])
                            # st.write("Remaining pieces to cut (count):", len(remaining_pieces))
                            # st.write("Remaining pieces list now:", remaining_pieces)

                            placed_in_this_pass = True
                            break
                    if placed_in_this_pass:
                        break
                if not placed_in_this_pass:
                    st.write("No more pieces fit in this sheet. Moving to next sheet.\n")
                    break

            cutting_plan.append(sheet)

        st.write(f"\n=== ✅ Final cutting plan uses {sheet_number} sheets ===")
        return cutting_plan

    def plot_cutting_plan(self, sheets):
        fig, axes = plt.subplots(1, len(sheets), figsize=(6 * len(sheets), 8))
        if len(sheets) == 1:
            axes = [axes]

        for sheet_index, (ax, sheet) in enumerate(zip(axes, sheets)):
            for cut in sheet['cuts']:
                ax.add_patch(plt.Rectangle(
                    (cut['x_offset'], cut['y_offset']),
                    cut['length'], cut['width'],
                    edgecolor='black', facecolor='orange', alpha=0.5
                ))
                ax.text(
                    cut['x_offset'] + cut['length'] / 2,
                    cut['y_offset'] + cut['width'] / 2,
                    f"{cut['length']}x{cut['width']}",
                    ha='center', va='center', fontsize=9, color='black'
                )
            ax.set_xlim(0, self.material_length)
            ax.set_ylim(0, self.material_width)
            ax.set_title(f"Sheet {sheet_index + 1}")
            ax.set_xlabel("Length (mm)")
            ax.set_ylabel("Width (mm)")

        plt.tight_layout()
        st.pyplot(fig)

def main():
    st.set_page_config(page_title="cut sheet spacecut", layout="centered")
    st.title("🛠️ cut sheet spacecut")

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
        length = st.number_input(f"Length of Piece {i + 1} (mm)", min_value=1, value=600, key=f"length_{i}")
        width = st.number_input(f"Width of Piece {i + 1} (mm)", min_value=1, value=300, key=f"width_{i}")
        quantity = st.number_input(f"Quantity of Piece {i + 1}", min_value=1, value=5, key=f"quantity_{i}")
        for _ in range(quantity):
            pieces.append({'length': length, 'width': width})

    # Submit button
    submitted = st.button("Generate Cutting Plan")
    if submitted:
        st.success("✅ Cutting Plan Generated")
        spacecut = Cutspacecut(material_length, material_width)
        sheets = spacecut.fit_pieces(pieces)

        # Show textual cutting plan
        st.subheader("🔷 Cutting Plan (Textual)")
        total_cut_area = 0
        total_material_area = 0
        sheet_count = len(sheets)

        for sheet_index, sheet in enumerate(sheets):
            st.write(f"Sheet {sheet_index + 1}:")
            for piece in sheet['cuts']:
                st.write(f"  Cut Piece: {piece['length']}mm x {piece['width']}mm at ({piece['x_offset']}mm, {piece['y_offset']}mm)")
                total_cut_area += piece['length'] * piece['width']
            total_material_area += material_length * material_width

        waste = total_material_area - total_cut_area
        #st.write(f"\nTotal Material Used: {total_cut_area} mm²")
        #st.write(f"Total Waste: {waste} mm²")
        st.write(f"\nTotal Sheets Used: {sheet_count}")

        # Visualization
        st.subheader("🔷 Cutting Plan (Visualization)")
        spacecut.plot_cutting_plan(sheets)

if __name__ == "__main__":
    main()
