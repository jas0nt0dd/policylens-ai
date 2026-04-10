"""
Document Parser — PyMuPDF + pdfplumber
Extracts text, clauses, tables, and metadata from policy PDFs/DOCXs.
"""
import re
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger("policylens.parser")


def parse_document(file_path: str) -> Dict[str, Any]:
    """
    Parse a PDF, DOCX, or TXT file.
    Returns structured document with sections, clauses, metadata.
    """
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return _parse_pdf(file_path)
    elif ext == ".docx":
        return _parse_docx(file_path)
    elif ext == ".txt":
        return _parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def _parse_pdf(file_path: str) -> Dict[str, Any]:
    """Extract text from PDF using PyMuPDF with pdfplumber fallback."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        full_text = ""
        pages = []
        for page_num, page in enumerate(doc):
            text = page.get_text("text")
            pages.append({"page": page_num + 1, "text": text})
            full_text += text + "\n"
        doc.close()

        metadata = _extract_metadata_from_text(full_text)
        sections = _split_into_sections(full_text)
        clauses = _extract_clauses(full_text)

        logger.info(f"PyMuPDF: {len(pages)} pages, {len(clauses)} clauses extracted")
        return {
            "source": file_path,
            "full_text": full_text,
            "pages": pages,
            "sections": sections,
            "clauses": clauses,
            "metadata": metadata,
            "parser": "pymupdf",
        }
    except ImportError:
        logger.warning("PyMuPDF not installed, falling back to pdfplumber")
        return _parse_pdf_plumber(file_path)
    except Exception as e:
        logger.error(f"PyMuPDF error: {e}")
        return _parse_pdf_plumber(file_path)


def _parse_pdf_plumber(file_path: str) -> Dict[str, Any]:
    """Fallback: extract text with pdfplumber (better for tables)."""
    try:
        import pdfplumber
        full_text = ""
        pages = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                pages.append({"page": i + 1, "text": text})
                full_text += text + "\n"

        metadata = _extract_metadata_from_text(full_text)
        sections = _split_into_sections(full_text)
        clauses = _extract_clauses(full_text)

        logger.info(f"pdfplumber: {len(pages)} pages, {len(clauses)} clauses extracted")
        return {
            "source": file_path,
            "full_text": full_text,
            "pages": pages,
            "sections": sections,
            "clauses": clauses,
            "metadata": metadata,
            "parser": "pdfplumber",
        }
    except Exception as e:
        logger.error(f"pdfplumber error: {e}")
        return _parse_txt_fallback(file_path)


def _parse_docx(file_path: str) -> Dict[str, Any]:
    """Extract text from DOCX using python-docx."""
    import docx
    doc = docx.Document(file_path)
    full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    sections = _split_into_sections(full_text)
    clauses = _extract_clauses(full_text)
    return {
        "source": file_path,
        "full_text": full_text,
        "pages": [],
        "sections": sections,
        "clauses": clauses,
        "metadata": _extract_metadata_from_text(full_text),
        "parser": "python-docx",
    }


def _parse_txt(file_path: str) -> Dict[str, Any]:
    """Parse plain text file."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        full_text = f.read()
    sections = _split_into_sections(full_text)
    clauses = _extract_clauses(full_text)
    return {
        "source": file_path,
        "full_text": full_text,
        "pages": [],
        "sections": sections,
        "clauses": clauses,
        "metadata": _extract_metadata_from_text(full_text),
        "parser": "plaintext",
    }


def _parse_txt_fallback(file_path: str) -> Dict[str, Any]:
    """Last resort: read as binary and decode."""
    try:
        with open(file_path, "rb") as f:
            raw = f.read()
        text = raw.decode("utf-8", errors="ignore")
        return {
            "source": file_path,
            "full_text": text,
            "pages": [],
            "sections": _split_into_sections(text),
            "clauses": _extract_clauses(text),
            "metadata": {},
            "parser": "fallback",
        }
    except Exception as e:
        raise RuntimeError(f"All parsers failed for {file_path}: {e}")


def _split_into_sections(text: str) -> List[Dict[str, Any]]:
    """Split document into numbered sections/articles."""
    # Match common section patterns: "Section 1", "Article 2", "Chapter 3", "1.", "1.1"
    pattern = re.compile(
        r"(?m)^((?:Section|Article|Chapter|Clause|Part|SECTION|ARTICLE|CHAPTER)\s+[\d\w]+\.?|[\d]+\.[\d]*\s+[A-Z])",
        re.MULTILINE,
    )
    splits = list(pattern.finditer(text))
    sections = []
    for i, match in enumerate(splits):
        start = match.start()
        end = splits[i + 1].start() if i + 1 < len(splits) else len(text)
        section_text = text[start:end].strip()
        sections.append({
            "id": f"section_{i+1}",
            "header": match.group().strip(),
            "text": section_text,
            "char_start": start,
            "char_end": end,
        })

    # If no sections found, treat whole doc as one section
    if not sections:
        sections = [{"id": "section_1", "header": "Document", "text": text, "char_start": 0, "char_end": len(text)}]

    return sections


def _extract_clauses(text: str) -> List[Dict[str, Any]]:
    """Extract individual sentences/clauses for analysis."""
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    clauses = []
    for i, sent in enumerate(sentences):
        sent = sent.strip()
        if len(sent) > 30:  # filter very short non-meaningful fragments
            clauses.append({
                "clause_id": f"clause_{i+1}",
                "text": sent,
                "index": i,
            })
    return clauses


def _extract_metadata_from_text(text: str) -> Dict[str, Any]:
    """Heuristically extract document metadata."""
    metadata = {}
    for line in text.splitlines()[:8]:
        cleaned = line.strip().strip("-: ")
        if len(cleaned.split()) >= 2 and 6 <= len(cleaned) <= 120:
            metadata["title"] = cleaned
            break

    year_match = re.search(r'\b(19|20)\d{2}\b', text[:500])
    if year_match:
        metadata["year"] = year_match.group()

    # Detect Indian policy keywords
    indian_keywords = ["Ministry", "Government of India", "Gazette", "Parliament", "Lok Sabha", "Rajya Sabha"]
    metadata["is_indian_policy"] = any(kw.lower() in text[:1000].lower() for kw in indian_keywords)

    # Language detection (basic)
    metadata["detected_language"] = "en"  # Default; translator service handles multilingual

    return metadata


def parse_url(url: str) -> Dict[str, Any]:
    """Fetch and parse text from a URL."""
    import requests
    from bs4 import BeautifulSoup
    resp = requests.get(url, timeout=15, headers={"User-Agent": "PolicyLens AI/1.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "html.parser")
    # Remove nav, header, footer noise
    for tag in soup(["nav", "header", "footer", "script", "style"]):
        tag.decompose()
    text = soup.get_text(separator="\n")
    text = re.sub(r'\n{3,}', '\n\n', text)
    sections = _split_into_sections(text)
    clauses = _extract_clauses(text)
    return {
        "source": url,
        "full_text": text,
        "pages": [],
        "sections": sections,
        "clauses": clauses,
        "metadata": _extract_metadata_from_text(text),
        "parser": "webscraper",
    }
