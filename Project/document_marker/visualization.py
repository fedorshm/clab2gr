import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import os
from config import BLOCK_COLORS

def visualize_annotations(pdf_path, annotations, page_num, output_image_dir=None):
    import fitz

    doc = fitz.open(pdf_path)
    page = doc.load_page(page_num)
    pix = page.get_pixmap()
    try:
        img = pix.pil_image()
    except AttributeError:
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    fig, ax = plt.subplots(1, figsize=(12, 12))
    ax.imshow(img)

    page_annotations = annotations.get(page_num, {})

    for block_type, blocks in page_annotations.items():
        color = BLOCK_COLORS.get(block_type, "black")
        for block in blocks:
            bbox = block['bbox']
            x0, y0, x1, y1 = bbox
            rect = patches.Rectangle((x0, y0), x1 - x0, y1 - y0, linewidth=2, edgecolor=color, facecolor='none')
            ax.add_patch(rect)
            ax.text(
                x0, y0 - 12, block_type,
                fontsize=10,
                color="white",
                verticalalignment='top',
                bbox=dict(
                    facecolor='black',
                    edgecolor='none',
                    pad=1
                )
            )

    plt.axis('off')

    if output_image_dir:
        os.makedirs(output_image_dir, exist_ok=True)
        base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        output_image_path = os.path.join(output_image_dir, f"{base_filename}_annotated_page_{page_num + 1}.png")
        plt.savefig(output_image_path, bbox_inches='tight', pad_inches=0)
        plt.close()
        print(f"Визуализированная аннотированная страница сохранена в {output_image_path}")
    else:
        plt.show()

    doc.close()
