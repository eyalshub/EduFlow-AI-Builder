# tests/core/normalizers/test_question_normalizer.py

import pytest
from copy import deepcopy
from app.core.normalizers.question_normalizer import normalize_mcq, shuffle_mcq_choices


def test_normalize_mcq_valid_input():
    q = {
        "stem": "מהי עיר הבירה של ספרד?",
        "choices": ["מדריד", "ברצלונה", "סביליה", "ולנסיה"],
        "correct_index": 0
    }

    result = normalize_mcq(deepcopy(q))
    assert result["correct_index"] == 0
    assert result["choices"][0] == "מדריד"
    assert "correctIndex" not in result


def test_normalize_mcq_supports_camelCase():
    q = {
        "stem": "מהי עיר הבירה של ספרד?",
        "choices": ["מדריד", "ברצלונה"],
        "correctIndex": 1  # camelCase key
    }

    result = normalize_mcq(deepcopy(q))
    assert result["correct_index"] == 1
    assert "correctIndex" not in result


def test_normalize_mcq_raises_if_missing_choices():
    q = {
        "stem": "מהי עיר הבירה של ספרד?",
        "correct_index": 0
    }

    with pytest.raises(ValueError, match="choices"):
        normalize_mcq(q)


def test_normalize_mcq_raises_if_choices_not_list():
    q = {
        "stem": "מהי עיר הבירה של ספרד?",
        "choices": "מדריד, ברצלונה",
        "correct_index": 0
    }

    with pytest.raises(ValueError, match="choices"):
        normalize_mcq(q)


def test_normalize_mcq_raises_if_missing_correct_index():
    q = {
        "stem": "מהי עיר הבירה של ספרד?",
        "choices": ["מדריד", "ברצלונה"]
    }

    with pytest.raises(ValueError, match="correct_index"):
        normalize_mcq(q)


def test_normalize_mcq_raises_if_correct_index_out_of_range():
    q = {
        "stem": "מהי עיר הבירה של ספרד?",
        "choices": ["מדריד", "ברצלונה"],
        "correct_index": 5
    }

    with pytest.raises(ValueError, match="out of range"):
        normalize_mcq(q)


def test_normalize_mcq_raises_if_stem_missing():
    q = {
        "choices": ["מדריד", "ברצלונה"],
        "correct_index": 0
    }

    with pytest.raises(ValueError, match="stem"):
        normalize_mcq(q)


def test_shuffle_mcq_preserves_correct_answer():
    q = {
        "stem": "מהי עיר הבירה של ספרד?",
        "choices": ["מדריד", "ברצלונה", "סביליה", "ולנסיה"],
        "correct_index": 0  # מדריד
    }

    shuffle_mcq_choices(q, seed=42)

    assert q["choices"] != ["מדריד", "ברצלונה", "סביליה", "ולנסיה"]
    assert "מדריד" in q["choices"]
    assert q["choices"][q["correct_index"]] == "מדריד"


def test_shuffle_mcq_does_nothing_on_single_choice():
    q = {
        "stem": "מהי עיר הבירה של ספרד?",
        "choices": ["מדריד"],
        "correct_index": 0
    }

    original = deepcopy(q)
    shuffle_mcq_choices(q)
    assert q == original
