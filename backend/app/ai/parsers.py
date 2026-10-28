import json
import re
from typing import Dict, Any, Optional


def clean_and_parse_json(text: str) -> Optional[Dict[str, Any]]:
    """Clean markdown code fences and parse JSON safely."""
    if not text:
        return None

    cleaned = text.strip()
    
    # Strip ```json ... ``` or ``` ... ```
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Attempt to extract outermost JSON object { ... }
        match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
    return None


def extract_text_from_file_bytes(content: bytes, filename: str) -> str:
    """Extract plain text from uploaded PDF, DOCX, or TXT file."""
    ext = filename.lower().split(".")[-1] if "." in filename else ""

    if ext == "pdf":
        try:
            import io
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(content))
            pages_text = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            return "\n".join(pages_text)
        except Exception as e:
            return f"Error reading PDF: {str(e)}"

    elif ext in ("docx", "doc"):
        try:
            import io
            from docx import Document
            doc = Document(io.BytesIO(content))
            return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        except Exception as e:
            return f"Error reading DOCX: {str(e)}"

    else:
        # Default text decode
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1", errors="ignore")
