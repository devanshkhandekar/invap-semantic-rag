import re
from typing import List, Dict

def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text

def dedupe_results(results: List[Dict], final_top_k: int) -> List[Dict]:
    seen = set()
    deduped = []

    for row in results:
        key = (
            row["document_id"],
            row["page_number"],
            normalize_text(row["chunk_text"][:180]),
        )
        if key in seen:
            continue

        seen.add(key)
        deduped.append(row)

        if len(deduped) >= final_top_k:
            break

    return deduped