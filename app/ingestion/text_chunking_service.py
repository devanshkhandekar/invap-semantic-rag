class TextChunkingService:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 120):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_pages(self, pages: list[dict]) -> list[dict]:
        chunks = []
        chunk_index = 0

        for page in pages:
            page_number = page["page_number"]
            text = page["text"]

            if not text.strip():
                continue

            page_chunks = self._split_text(text)

            for chunk in page_chunks:
                chunks.append({
                    "chunk_index": chunk_index,
                    "page_number": page_number,
                    "chunk_text": chunk
                })
                chunk_index += 1

        return chunks

    def _split_text(self, text: str) -> list[str]:
        words = text.split()
        if not words:
            return []

        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            additional_length = len(word) + 1

            if current_length + additional_length > self.chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))

                overlap_words = self._get_overlap_words(current_chunk)
                current_chunk = overlap_words[:]
                current_length = len(" ".join(current_chunk))

            current_chunk.append(word)
            current_length += additional_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _get_overlap_words(self, words: list[str]) -> list[str]:
        if not words:
            return []

        overlap_words = []
        running_length = 0

        for word in reversed(words):
            word_len = len(word) + 1
            if running_length + word_len > self.chunk_overlap:
                break
            overlap_words.append(word)
            running_length += word_len

        return list(reversed(overlap_words))