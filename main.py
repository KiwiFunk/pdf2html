import sys
from parser import inspect_pdf

"""
argv is a list of command-line arguments.
argv[0] is the script name (main.py).
argv[1] should be the path to the PDF file to inspect.
Usage: py main.py ./assets/test.pdf
"""
def main():
    if len(sys.argv) < 2:
        print("Valid argument required: path to PDF document")
        return

    pdf_path = sys.argv[1]
    inspect_pdf(pdf_path, image_output_dir="images")

if __name__ == "__main__":
    main()