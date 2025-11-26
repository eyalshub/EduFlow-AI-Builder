# app/utils/hash.py
import hashlib

def generate_cache_key(topic_name: str, subject: str, grade_level: str, big_idea: str) -> str:
    """
    Generates a unique SHA256 hash from key input fields.
    """
    key_string = f"{topic_name}_{subject}_{grade_level}_{big_idea}"
    return hashlib.sha256(key_string.encode()).hexdigest()
