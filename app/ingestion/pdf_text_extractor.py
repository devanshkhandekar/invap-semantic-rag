from pathlib import Path
from pypdf import PdfReader
from langdetect import detect, LangDetectException


class PDFTextExtractor:
    def extract(self, pdf_path: str) -> dict:
        pdf_file = Path(pdf_path)
        reader = PdfReader(str(pdf_file))

        pages = []
        full_text_parts = []

        for page_index, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            cleaned_text = self._clean_text(page_text)

            pages.append({
                "page_number": page_index,
                "text": cleaned_text
            })

            if cleaned_text.strip():
                full_text_parts.append(cleaned_text)

        combined_text = "\n".join(full_text_parts)
        language = self._detect_language(combined_text)

        return {
            "filename": pdf_file.name,
            "source_path": str(pdf_file.resolve()),
            "page_count": len(reader.pages),
            "language": language,
            "pages": pages
        }

    @staticmethod
    def _clean_text(text: str) -> str:
        if not text:
            return ""

        text = text.replace("\x00", " ")
        text = text.replace("\r", "\n")

        lines = [line.strip() for line in text.split("\n")]
        lines = [line for line in lines if line]

        return "\n".join(lines).strip()

    @staticmethod
    def _detect_language(text: str) -> str:
        sample = text[:2000].strip()
        if not sample:
            return "unknown"

        try:
            return detect(sample)
        except LangDetectException:
            return "unknown"