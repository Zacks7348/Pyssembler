def process_escape_chars(s: str) -> str:
    return bytes(s, 'utf-8').decode('unicode_escape')