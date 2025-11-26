from typing import List, Tuple, Optional, Dict
import uuid
import json


def generate_uuid() -> str:
    return str(uuid.uuid4())


def format_html(text: str) -> str:
    return f'<p fontsize="18px" textalign="inherit" class="!my-0.5 !py-0 mb-4 body" ' \
           f'style="text-align: inherit; font-size: 18px" font-size="18px">{text}</p>'


def _get_feedback_levels() -> List[Dict]:
    return [
        {"code": "failed", "value": 0, "feedback": ""},
        {"code": "partial", "range": [1, 50], "feedback": ""},
        {"code": "decent", "range": [51, 79], "feedback": ""},
        {"code": "good", "range": [80, 89], "feedback": ""},
        {"code": "great", "range": [90, 99], "feedback": ""},
        {"code": "perfect", "value": 100, "feedback": ""}
    ]


def build_mcq_question(
    stem: str,
    options: List[str],
    correct_index: int,
    *,
    question_id: Optional[str] = None,
    page_id: Optional[str] = None,
    section_id: Optional[str] = None,
    exercise_id: Optional[str] = None,
    play_id: Optional[str] = None,
    position: int = 1,
    multi_select: bool = False
) -> Dict:

    return {
        "image": "choice-block",
        "name": "choice",
        "type": "question",
        "content": {
            "type": "text",
            "title": "",
            "subTitle": format_html(stem),
            "min": 1,
            "max": 1,
            "options": [
                {
                    "id": generate_uuid(),
                    "title": format_html(opt),
                    "correct": i == correct_index
                } for i, opt in enumerate(options)
            ],
            "shuffle": True,
            "keyboardSettings": {
                "showMathmaticalKeyboard": False,
                "keyboardList": ["BASIC", "numeric", "alphabetic"]
            },
            "fit": "full",
            "multiSelect": multi_select,
            "layout": "horizontal",
            "format": "button"
        },
        "settings": {
            "type": "default",
            "submissionStyle": "inline",
            "optional": False
        },
        "id": question_id or generate_uuid(),
        "page": page_id or generate_uuid(),
        "section": section_id or generate_uuid(),
        "position": position,
        "completion": {
            "coins": 0,
            "feedback_enabled": True,
            "levels": _get_feedback_levels()
        },
        "exercise": exercise_id or generate_uuid(),
        "metadata": {
            "titleVisible": True,
            "subTitleVisible": True
        },
        "play": play_id or generate_uuid()
    }


def build_matching_question(
    pairs: List[Tuple[str, str]],  # רשימת זוגות התאמה: (שאלה, תשובה)
    *,
    question_id: Optional[str] = None,
    page_id: Optional[str] = None,
    section_id: Optional[str] = None,
    exercise_id: Optional[str] = None,
    play_id: Optional[str] = None,
    position: int = 1,
    stem: Optional[str] = None,
) -> Dict:

    # צור מזהי UUID לתשובות (matches)
    match_ids = [generate_uuid() for _ in pairs]
    match_blocks = [
        {
            "id": mid,
            "format": "image-text",
            "title": format_html(answer),
            "image": ""
        }
        for (_, answer), mid in zip(pairs, match_ids)
    ]

    option_blocks = [
        {
            "id": generate_uuid(),
            "format": "image-text",
            "title": format_html(question),
            "image": "",
            "matches": [mid]
        }
        for (question, _), mid in zip(pairs, match_ids)
    ]

    return {
        "image": "pairing-block",
        "name": "pairing",
        "type": "question",
        "content": {
            "title": "",
            "subTitle": format_html(stem) if stem else "",
            "display": "columns",
            "optionsName": "",
            "matchesName": "",
            "options": option_blocks,
            "matches": match_blocks
        },
        "tags": [],
        "id": question_id or generate_uuid(),
        "play": play_id or generate_uuid(),
        "page": page_id or generate_uuid(),
        "section": section_id or generate_uuid(),
        "position": position,
        "settings": {
            "optional": False,
            "type": "default",
            "submissionStyle": "inline"
        },
        "completion": {
            "coins": 0,
            "feedback_enabled": True,
            "levels": _get_feedback_levels()
        },
        "exercise": exercise_id or generate_uuid(),
        "metadata": {
            "titleVisible": True,
            "subTitleVisible": True
        }
    }


def build_open_question(
    stem: str,
    *,
    question_id: Optional[str] = None,
    page_id: Optional[str] = None,
    section_id: Optional[str] = None,
    exercise_id: Optional[str] = None,
    play_id: Optional[str] = None,
    position: int = 1,
    placeholder: str = "כתבו את תשובתכם כאן"
) -> Dict:

    return {
        "image": "free_text",
        "name": "free_text",
        "type": "question",
        "content": {
            "multi": False,
            "title": "",
            "subTitle": format_html(stem),
            "placeholder": placeholder,
            "text": "",
            "editable": True,
            "keyboardSettings": {
                "showMathmaticalKeyboard": False,
                "keyboardList": ["BASIC", "numeric", "alphabetic"]
            }
        },
        "id": question_id or generate_uuid(),
        "play": play_id or generate_uuid(),
        "page": page_id or generate_uuid(),
        "section": section_id or generate_uuid(),
        "position": position,
        "settings": {
            "optional": False,
            "type": "default",
            "submissionStyle": "inline",
            "aiFeedbackEnabled": True
        },
        "completion": {
            "coins": 0,
            "feedback_enabled": True,
            "levels": _get_feedback_levels()
        },
        "exercise": exercise_id or generate_uuid(),
        "metadata": {
            "titleVisible": True,
            "subTitleVisible": True
        }
    }



def build_rich_text_paragraph_block(
    text: str,
    placeholder: str = "כיתבו את הפסקה שלכם כאן",
    block_id: Optional[str] = None,
    play_id: Optional[str] = None,
    page_id: Optional[str] = None,
    section_id: Optional[str] = None,
    position: int = 1
) -> Dict:
    return {
        "name": "rich_text",
        "type": "content",
        "content": {
            "data": {
                "type": "doc",
                "content": [
                    {
                        "type": "paragraph",
                        "attrs": {
                            "indent": None,
                            "color": None,
                            "dir": None,
                            "textAlign": "inherit",
                            "class": "mb-4 body",
                            "fontSize": "18px"
                        },
                        "content": [
                            {
                                "type": "text",
                                "text": text.strip()
                            }
                        ]
                    }
                ]
            },
            "placeholder": placeholder
        },
        "id": block_id or generate_uuid(),
        "play": play_id or generate_uuid(),
        "page": page_id or generate_uuid(),
        "section": section_id or generate_uuid(),
        "position": position,
        "settings": {
            "optional": False
        },
        "completion": {
            "coins": 0
        }
    }

if __name__ == "__main__":
    from pprint import pprint
    mcp_question = build_mcq_question(
        stem="מהי עיר הבירה של אנגליה?",
        options=["לונדון", "פריז", "רומא", "ברלין"],
        correct_index=1,
        question_id="afb117c6-32ba-4325-af36-ca5290ce87d6",
        page_id="f98d5626-0843-42c1-a836-611ef25b9751",
        section_id="d6fa308a-c48b-4abb-9674-c78cb6f1582a",
        exercise_id="9ff9835a-a090-413a-b30a-fa2d10a1ace5",
        play_id="b1dca3b6-8aa2-475b-96d8-ec04791a010c",
        position=1,
        multi_select=False
    )
    pprint(mcp_question)

    open_question = build_open_question(
    stem="מה הייתה השפעתה של המפכה הצרפתית ? איך היא השפיעה על החברה ?",
    question_id="68a433de315dea8113f61df2",
    page_id="688b38a3a4f266618ba27640",
    section_id="688b38a3a4f266618ba2763f",
    exercise_id="68a433de315dea8113f61df3",
    play_id="682add5a80c45e0226a2ec46",
    position=2
)
    
    matching_question = build_matching_question(
    stem="התאימו בין האירוע המרכזי לבין התוצאה או המאפיין שלו",
    pairs=[
        ("קריסת הסמכות המלוכנית", "התרחשה בשנת 1789"),
        ("כיבוש הבסטיליה", "היה מעשה של ההמון"),
        ("הכרזת הצהרת זכויות האדם", "סימלה שינוי מהפכני"),
    ],
    question_id="68a43547315dea8113f61e0a",
    page_id="688b38a3a4f266618ba27640",
    section_id="688b38a3a4f266618ba2763f",
    exercise_id="68a43547315dea8113f61e0b",
    play_id="682add5a80c45e0226a2ec46",
    position=3
)
    text_editor = build_rich_text_paragraph_block(
    text="המהפכה הצרפתית סימלה מעבר לשלטון עממי ודמוקרטי.",
    placeholder="כיתבו את הפסקה שלכם כאן",
    block_id="68a43939315dea8113f61e0c",
    play_id="682add5a80c45e0226a2ec46",
    page_id="688b38a3a4f266618ba27640",
    section_id="688b38a3a4f266618ba2763f",
    position=3
)
    with open("text_editor.json", "w", encoding="utf-8") as f:
        json.dump(text_editor, f, ensure_ascii=False, indent=2)