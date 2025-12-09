import re
import csv
from typing import BinaryIO
import pymupdf


def _text_norm(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text

def _get_pdf_text(pdf_doc: BinaryIO) -> str:
    if pdf_doc is None:
        raise ValueError("No se proporcionó un archivo PDF.")
    try:
        pdf_doc.seek(0)
    except Exception:
        raise ValueError("El archivo subido no es un objeto seekable.")

    header = pdf_doc.read(5)
    if not isinstance(header, (bytes, bytearray)) or not header.startswith(b"%PDF-"):
        raise ValueError("El archivo no parece ser un PDF válido.")

    pdf_doc.seek(0)
    data = pdf_doc.read()
    if not data:
        raise ValueError("El PDF está vacío o es ilegible.")

    pages_text = []
    try:
        with pymupdf.open(stream=data, filetype="pdf") as doc:
            for idx, page in enumerate(doc):
                try:
                    content = page.get_text() or ""
                except Exception as e:
                    print(f"⚠️ No se pudo extraer la página {idx+1}: {e}")
                    content = ""

                if content.strip():
                    pages_text.append(f"\n\n=== [PAGE {idx+1}] ===\n\n{content}")
    except Exception:
        raise ValueError("Error leyendo el PDF. Archivo corrupto o no soportado.")

    text = "".join(pages_text)
    if not text.strip():
        raise ValueError("No se encontró texto extraíble en el PDF.")
    return _text_norm(text)

def _csv_to_text(csv_file):
    csv_file.seek(0)
    text = csv_file.read().decode("utf-8")
    reader = csv.DictReader(text.splitlines())
    rows_text = []
    for idx, row in enumerate(reader):
        row_content = f"\n\n=== [ROW {idx + 1}] ===\n\n" + " | ".join(f"{k}: {v}" for k, v in row.items())
        rows_text.append(row_content)
    text = "".join(rows_text)

    print("XXXXXXXXXXXXXXXXX")
    print(text)
    if not text.strip():
        raise ValueError("No se encontró texto extraíble en el CSV.")
    return _text_norm(text)