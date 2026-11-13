"""PRD AC-12, ADR-003 §5.1, §5.4, §8 'Brak wycieku': the request carries only neutral text and the image."""
import base64
import io
import json

from PIL import Image

from map_qa.photo_reading.image import prepare_bytes
from map_qa.photo_reading.payload import chat_payload, chat_schema, decisions_payload
from map_qa.photo_reading.questions import QUESTIONS, STATE_TEXT

PHOTO_ID = "panoramax_334a574d-18cb-4c2e-be3f-f99307e080d9"
FORBIDDEN = [PHOTO_ID, ".jpg", "offline/", "\"certain\"", "uncertain", "paved_label", "regulatory--maximum-speed-limit",
             "maxspeed", "50.018549", "20.126139972", "czecko", "2026-07-21", "osm_way_id", "mapillary"]


def image_with_gps():
    img = Image.new("RGB", (800, 600), (10, 120, 10))
    exif = Image.Exif()
    exif[0x8825] = {2: (50.0, 1.0, 6.0), 4: (20.0, 7.0, 34.0)}
    exif[0x010E] = PHOTO_ID  # ImageDescription containing the photo id
    buf = io.BytesIO()
    img.save(buf, "JPEG", exif=exif.tobytes())
    return prepare_bytes(buf.getvalue())


def test_decisions_payload_exact_shape():
    img = image_with_gps()
    p = decisions_payload("openai/gpt-6-luna-decisions", "photo", img,
                          ["surface", "junction_visible", "street_lighting_visible"])
    assert set(p) == {"model", "state", "questions"}
    assert len(p["state"]) == 2 and p["state"][0] == STATE_TEXT["photo"]
    part = p["state"][1]
    assert part["type"] == "image_url" and part["image_url"]["url"].startswith("data:image/jpeg;base64,")
    assert set(p["questions"]) == {"surface", "junction_visible", "street_lighting_visible"}
    q = p["questions"]["surface"]
    assert q == {"type": "choice", "instructions": QUESTIONS["surface"]["instructions"],
                 "criteria": QUESTIONS["surface"]["criteria"]}


def test_no_leak_in_serialized_payloads():
    img = image_with_gps()
    for payload in (decisions_payload("m", "photo", img, ["surface"]),
                    chat_payload("m2", "photo", img, ["surface", "junction_visible"]),
                    decisions_payload("m", "sign_crop", img, ["speed_limit_value"])):
        text = json.dumps(payload)
        for bad in FORBIDDEN:
            assert bad not in text, bad
        for key in ("provider", "session_id", "trace", "user", "assets", "reasoning_effort"):
            assert key not in payload  # optional API fields are never sent (ADR-003 §5.1, §5.4)


def test_image_bytes_have_no_exif_gps_or_description():
    img = image_with_gps()
    payload = decisions_payload("m", "photo", img, ["surface"])
    data = base64.b64decode(payload["state"][1]["image_url"]["url"].split(",", 1)[1])
    assert data == img.data
    assert not Image.open(io.BytesIO(data)).getexif()
    assert PHOTO_ID.encode() not in data


def test_chat_payload_shape():
    img = image_with_gps()
    p = chat_payload("openai/gpt-6-luna", "photo", img, ["junction_visible", "surface"])
    assert set(p) == {"model", "messages", "reasoning", "response_format"}
    assert p["reasoning"] == {"effort": "medium"}
    msg = p["messages"]
    assert len(msg) == 1 and msg[0]["role"] == "user"
    kinds = [c["type"] for c in msg[0]["content"]]
    assert kinds == ["text", "image_url"]
    rf = p["response_format"]
    assert rf["type"] == "json_schema" and rf["json_schema"]["strict"] is True
    schema = rf["json_schema"]["schema"]
    assert schema == chat_schema(["junction_visible", "surface"])


def test_chat_schema_closed():
    s = chat_schema(["speed_limit_value"])
    assert s["additionalProperties"] is False and s["required"] == ["speed_limit_value"]
    item = s["properties"]["speed_limit_value"]
    assert item["additionalProperties"] is False and item["required"] == ["answer", "certainty"]
    assert "unreadable" in item["properties"]["answer"]["enum"] and "none" in item["properties"]["answer"]["enum"]
    assert item["properties"]["certainty"]["enum"] == ["high", "medium", "low"]
