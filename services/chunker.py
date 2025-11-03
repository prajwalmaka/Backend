from typing import List




def chunk_by_paragraphs(text: str) -> List[str]:




    raw_pars = [p.strip() for p in text.split("\n\n")]


    pars = []
    for p in raw_pars:
        if not p:
            continue

        p = p.replace("\n", " ").strip()
        if p:
            pars.append(p)
    return pars



def chunk_by_size(text: str, size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Fixed-size character window chunking with optional overlap.
    size: chunk size in characters
    overlap: number of characters to overlap between chunks
    """
    if size <= 0:
        raise ValueError("size must be positive")
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")

    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = min(start + size, text_len)
        chunks.append(text[start:end].strip())
        if end == text_len:
            break
        start = end - overlap
    # filter out empty
    return [c for c in chunks if c]