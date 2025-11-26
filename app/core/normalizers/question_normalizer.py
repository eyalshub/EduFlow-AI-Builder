# app/core/normalizers/question_normalizer.py
from typing import Dict, Any, List, Optional
import random


def normalize_mcq(question: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize an MCQ question to an internal canonical schema and validate it.

    Required normalized shape (after this function returns):
      {
        "stem": str (non-empty),
        "choices": List[str] (non-empty),
        "correct_index": int (0 <= idx < len(choices)),
        ... (optional fields like "explanation")
      }

    Supports both snake_case and camelCase for correct index:
      - 'correct_index' (preferred internal key)
      - 'correctIndex' (will be converted to 'correct_index')
    """
    q = question or {}

    # Validate choices list
    choices = q.get("choices")
    if not isinstance(choices, list) or len(choices) == 0:
        raise ValueError("MCQ must include a non-empty 'choices' list")

    # Pull and normalize 'correct_index'
    idx = q.get("correct_index", q.get("correctIndex"))
    if idx is None:
        raise ValueError("MCQ must include 'correct_index' (or 'correctIndex')")
    try:
        idx = int(idx)
    except Exception as e:
        raise ValueError(f"MCQ 'correct_index' must be an integer: {e}")

    if idx < 0 or idx >= len(choices):
        raise ValueError("MCQ 'correct_index' is out of range for the given 'choices'")

    q["correct_index"] = idx
    if "correctIndex" in q:
        # Keep only the canonical snake_case key internally
        del q["correctIndex"]

    # Validate stem
    stem = q.get("stem")
    if not isinstance(stem, str) or not stem.strip():
        raise ValueError("MCQ must include a non-empty 'stem'")

    # Optional cleanup (avoid null fields)
    if "explanation" in q and q["explanation"] is None:
        del q["explanation"]

    return q


def shuffle_mcq_choices(question: Dict[str, Any], seed: Optional[int] = None) -> Dict[str, Any]:
    """
    Shuffle MCQ choices in-place and update 'correct_index' accordingly.

    Notes:
      - Call 'normalize_mcq' before this to ensure question is valid.
      - 'seed' can be provided for deterministic shuffling in tests.
    """
    q = question
    choices: List[Any] = q.get("choices", [])
    if not isinstance(choices, list) or len(choices) < 2:
        # Nothing to shuffle (0/1 choice or invalid structure)
        return q

    idx = q.get("correct_index")
    if not isinstance(idx, int):
        # Should not happen if normalize_mcq was called first
        return q

    rng = random.Random(seed)
    # Pair each choice with its original index so we can find the new correct index
    paired = list(enumerate(choices))
    rng.shuffle(paired)

    q["choices"] = [text for _, text in paired]
    q["correct_index"] = next(i for i, (orig_idx, _) in enumerate(paired) if orig_idx == idx)
    return q


def is_dup_by_stem(question_a: Dict[str, Any], question_b: Dict[str, Any]) -> bool:
    """
    Consider two questions duplicates if their 'stem' strings match exactly (after strip()).
    This is a simple heuristic; you can make it more robust (e.g., fuzziness) if needed.
    """
    a = (question_a.get("stem") or "").strip()
    b = (question_b.get("stem") or "").strip()
    return a != "" and a == b
