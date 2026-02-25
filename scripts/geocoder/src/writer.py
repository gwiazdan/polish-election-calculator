import json

def append_to_jsonl(data, filepath):
    """Append single record to JSONL file."""
    serialized = {
        key: (value.wkt if hasattr(value, "wkt") else value)
        for key, value in data.items()
    }
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(serialized, ensure_ascii=False) + "\n")