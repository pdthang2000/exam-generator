import PyPDF2
from pptx import Presentation


def parse_pdf(file_path):
    reader = PyPDF2.PdfReader(file_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def parse_pptx(file_path):
    prs = Presentation(file_path)
    texts = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                texts.append(shape.text_frame.text)
    return "\n".join(texts)


def parse_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


PARSERS = {
    "pdf": parse_pdf,
    "pptx": parse_pptx,
    "txt": parse_txt,
}


def parse_file(file_path, file_type):
    parser = PARSERS.get(file_type)
    if not parser:
        raise ValueError(f"Unsupported file type: {file_type}")
    return parser(file_path)
