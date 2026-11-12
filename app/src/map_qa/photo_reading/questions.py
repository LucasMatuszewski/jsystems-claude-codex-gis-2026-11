"""Question set qs-v1 (ADR-003 §4.1). Neutral English text; any change bumps the version and invalidates cache."""
from __future__ import annotations

QUESTION_SET_VERSION = "qs-v1"

STATE_TEXT = {
    "photo": "A photograph taken from a street-level camera.",
    "sign_crop": "A cropped image from a street-level photograph.",
}

SPEED_VALUES = ["5", "10", "15", "20", "25", "30", "40", "50", "60", "70", "80", "90", "100", "110", "120", "130",
                "140"]

QUESTIONS: dict[str, dict] = {
    "surface": {
        "applies_to": "photo",
        "instructions": "What is the surface of the main road visible in the photo?",
        "criteria": {
            "paved": "asphalt, concrete or paving stones/sett",
            "unpaved": "gravel, dirt, grass, sand or compacted earth",
            "unknown": "the road surface is not visible or cannot be determined",
        },
    },
    "junction_visible": {
        "applies_to": "photo",
        "instructions": "Is a junction of roads for vehicles visible in the photo?",
        "criteria": {
            "yes": "two or more roads for vehicles visibly join or split",
            "no": "no such junction is visible (a pedestrian crossing or an overpass alone is not a junction)",
            "unknown": "cannot be determined",
        },
    },
    "street_lighting_visible": {
        "applies_to": "photo",
        "instructions": "Is a street lamp fitting visible in the photo?",
        "criteria": {
            "yes": "a recognizable street lamp fitting is visible",
            "no": "no street lamp fitting is visible (a utility pole alone does not count)",
            "unknown": "cannot be determined",
        },
    },
    "speed_limit_value": {
        "applies_to": "sign_crop",
        "instructions": ("What maximum speed value is shown on a round speed limit sign with a red border "
                         "(Polish B-33) in the image?"),
        "criteria": {
            **{v: "the value on a B-33 sign" for v in SPEED_VALUES},
            "none": "no B-33 sign is visible (zone signs, end-of-limit signs and other signs count as none)",
            "unreadable": "a B-33 sign is visible but its value cannot be read",
        },
    },
}


def questions_for(kind: str) -> list[str]:
    return [qid for qid, q in QUESTIONS.items() if q["applies_to"] == kind]


def options(qid: str) -> list[str]:
    return list(QUESTIONS[qid]["criteria"])
