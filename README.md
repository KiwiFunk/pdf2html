# pdf2html
Convert MailerLite-style PDF newsletters into clean, semantic HTML for use in a CMS, with accessible images and anchor links.


## Project overview

- **Goal:** A standalone Windows `.exe` that takes a MailerLite PDF newsletter and outputs a formatted `newsletter.html` file.
- **User flow:**
  - **Input:** User drags a PDF onto the app or selects it via a simple GUI.
  - **Process:** App parses the PDF, detects sections, text, images, and links.
  - **Output:** App writes `newsletter.html` in the same folder. User copies HTML into their CMS.
- **Maintenance:** Zero install for end users. The `.exe` ships with everything bundled.

## Tech stack

| Layer | Tool | Why |
|------|------|-----|
| Language | **Python 3.11+** | Rapid parsing/templating ecosystem |
| PDF parsing | **PyMuPDF (fitz)** | Reliable text, image, and link extraction in one library |
| HTML generation | **Jinja2** (or string templates) | Clean templates and maintainable markup |
| GUI (optional) | **Tkinter** | Built-in, simple file picker or drag-and-drop |
| Packaging | **PyInstaller** | One-file `.exe` with bundled dependencies |

> Users receive a single `.exe`. Python and libraries are bundled at build time; no installs are required.

## Architecture plan

### 1. Input layer

- **Accept:** `.pdf` via drag-and-drop on the `.exe` or a file picker dialog.
- **Validate:**
  - **File type:** Ensure `.pdf`.
  - **Structure hints:** Basic sanity checks (pages > 0, text present).
- **Config (optional):**
  - **Image output:** Choose folder or embed as base64.
  - **CMS image path:** Map local image filenames to site-relative URLs.

### 2. Parsing layer

- **Text extraction:** Use `page.get_text("dict")` to access blocks/lines/spans with positions and font sizes.
- **Heading detection:** Identify headers by larger font size or consistent Y regions (Mailerlite is predictable).
- **Links:**
  - **Text links:** `page.get_links()` provides rectangles and target URIs.
  - **Image links:** Pair link rectangles with image rectangles to wrap images in anchor tags.
- **Images:**
  - **List:** `page.get_images()` returns image references and positions.
  - **Extract:** Render via `fitz.Pixmap` and save as `.png` (or base64 embed).
- **Grouping:** Build `NewsletterSection` objects with title, body, anchors, and linked images.

### 3. Content model

- **NewsletterSection:**
  - **Title:** Section heading text.
  - **Body:** Combined paragraphs in reading order.
  - **AnchorId:** Slugified from title for in-page anchors.
  - **Images:** List of `{ image_path/base64, link_url, alt_text }`.

### 4. HTML generator

- **Template-driven:** Use Jinja2 to render semantic HTML.
- **Structure:**
  - **Sections:** `<section aria-labelledby="...">`
  - **Headings:** `<h2 id="...">`
  - **Images:** `<a href="..."><img src="..." alt="..." /></a>` when linked; otherwise plain `<img>`.
  - **Accessibility:** `aria-label` on anchors, descriptive `alt` text for images, logical heading order.

### 5. Output layer

- **Write:** `newsletter.html` in the same folder as the input PDF.
- **Assets:**
  - **Images:** Saved to `images/` next to HTML or embedded as base64.
- **Feedback:** Console or GUI message: “HTML generated at …”

## PDF parsing strategy

### Step-by-step

1. **Extract text blocks with coordinates and font sizes**
   - **Method:** `page.get_text("dict")`
   - **Heuristic:**
     - **Heading spans:** Font size above a measured threshold (e.g., top-tier sizes in page 1).
     - **Body spans:** Normalized size range.

2. **Group content into sections**
   - **Start new section:** When a heading-like span appears.
   - **Aggregate body:** Append subsequent spans until the next heading.

3. **Detect hyperlinks**
   - **Get all links:** `page.get_links()` returns rectangles + URIs.
   - **Text link pairing:** Match link rectangles to nearby text spans.
   - **Image link pairing:** Match link rectangles to image rectangles (center-in-rect or overlap test).

4. **Handle images**
   - **List and render:** `page.get_images()` → `fitz.Pixmap` → save `.png`.
   - **Alt text strategy:** Prefer nearby caption or section title; fallback to a safe description.
   - **Anchor wrapping:** If a link overlaps an image, wrap `<img>` in `<a href="...">`.

5. **Generate anchor IDs**
   - **Slugify titles:** Lowercase, replace spaces with `-`, strip punctuation.
   - **Apply anchors:** `<h2 id="anchor">`, `<section aria-labelledby="anchor">`.

## HTML output goals

- **Semantic tags:** `<section>`, `<h2>`, `<p>`, `<a>`, `<img>`.
- **Accessibility:**
  - **Images:** `alt` is descriptive, no “image of”. Allow users to input aria?
  - **Links:** `aria-label` clarifies action or destination where needed.
  - **Headings:** Logical hierarchy and readable order.
- **Navigation:** In-page anchors for section titles and optional table of contents.
- **Clean formatting:** Indented, readable, minimal inline styles.

Example block:
```html
<section aria-labelledby="section-title">
  <h2 id="section-title">Title</h2>
  <a href="https://example.com" aria-label="Learn More">
      <img src="images/article1.png" alt="Article Hero Image" />
  </a>
  <p>Body text...</p>
</section>
```

## Testing plan

- **Samples:** 3–5 MailerLite PDFs covering typical newsletter variants.
- **Validate:**
  - **Section detection:** Titles and body grouped correctly.
  - **Image extraction:** Files saved or base64 embedded; paths correct.
  - **Link fidelity:** Text and image links preserved; image-link pairing works.
  - **Anchors:** Slug generation is consistent; TOC links navigate correctly.
  - **Accessibility:** Alt text defaults make sense; `aria` labels applied where helpful.
- **Cross-device preview:** Open HTML in desktop, tablet, and mobile browsers to check flow, scaling, and readability.

## Deployment plan

- **Package:** Build a one-file `.exe` using PyInstaller.
  - Command: `pyinstaller --onefile --add-data "templates;templates" --add-data "assets;assets" main.py`
- **Delivery:** Provide the `.exe` and a short README: “Drag your PDF onto this file or double-click and select a PDF.”
- **Optional polish:**
  - **Icon:** `--icon icon.ico`
  - **Versioning:** `--version-file file.txt`
  - **Folder mode:** Build a one-folder distribution if large images are expected and you prefer external files.

