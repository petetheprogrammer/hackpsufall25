import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def load_lesson_pack(subject, grade, locale):
    """Load lesson JSON for given subject, grade, locale."""
    file_path = BASE_DIR / 'data' / 'lessons' / locale / subject / f'grade{grade}.json'
    if not file_path.exists():
        raise FileNotFoundError(f"Lesson file not found: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_lesson_pack(data):
    """Basic validation of lesson JSON structure."""
    required_keys = ['subject', 'grade', 'locale', 'units']
    if not all(key in data for key in required_keys):
        raise ValueError("Invalid lesson pack structure")
    for unit in data['units']:
        if 'id' not in unit or 'title' not in unit or 'cards' not in unit or 'quiz' not in unit:
            raise ValueError("Invalid unit structure")
    return True