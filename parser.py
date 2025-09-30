# parser.py
import os
import fitz  # PyMuPDF

def inspect_pdf(pdf_path: str, image_output_dir: str = "images"):
    """
    Inspect a PDF and print:
    - Text spans with font sizes and bounding boxes
    - Link annotations with URIs and rectangles
    - Extracted images saved to disk
    """
    os.makedirs(image_output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc[page_num]
        print(f"--- Page {page_num + 1} ---")

        text_dict = page.get_text("dict")
        for block in text_dict.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "")
                    size = span.get("size", 0.0)
                    bbox = span.get("bbox", [0, 0, 0, 0])  # [x0, y0, x1, y1]
                    
                    if text.strip():
                        print(f"Text: {text} | Size: {size:.2f} | "
                              f"Box: x0={bbox[0]:.2f}, y0={bbox[1]:.2f}, x1={bbox[2]:.2f}, y1={bbox[3]:.2f}")

        for link in page.get_links():
            uri = link.get("uri")
            rect = link.get("from")  # fitz.Rect
            if uri:
                # Rect prints as 'Rect(x0, y0, x1, y1)'
                print(f"Link: {uri} | Rect: {rect}")

        # Handle Images
        for idx, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                # Convert CMYK or images with alpha to RGB for wide compatibility
                if pix.n >= 4:  # has alpha or is CMYK
                    rgb = fitz.Pixmap(fitz.csRGB, pix)
                    pix = rgb
                img_path = os.path.join(image_output_dir, f"page{page_num + 1}_img{idx + 1}.png")
                pix.save(img_path)
                print(f"Image saved: {img_path}")
                pix = None  # allow GC to free memory
            except Exception as e:
                print(f"Image extraction error (xref {xref}): {e}")

    doc.close()