"""ADR-004 §3.1, §3.3; ADR-003 §5.8: capture prints cost/limit, asks y/N, sends exactly one request."""
import io

import pytest

from map_qa.core.config import load_config
from map_qa.photo_reading.capture_cli import run_model_capture
from map_qa.photo_reading.clients import ApiResult


class CountingClient:
    def __init__(self):
        self.calls = []

    def post(self, path, payload):
        self.calls.append((path, payload["model"]))
        return ApiResult(200, {"answers": {}, "model": payload["model"], "usage": {"cost": 0.0001}}, {}, 5.0)

    def close(self):
        pass


@pytest.fixture()
def cfg(tmp_path, data_dir):
    return load_config({"work_dir": tmp_path / "work", "data_dir": data_dir}, {})


def run(cfg, tmp_path, kind, answer, image=None):
    client = CountingClient()
    out = io.StringIO()
    code = run_model_capture(cfg, {"OPENROUTER_API_KEY": "k"}, kind=kind, yes=False, image=image, name=None,
                             captures_dir=tmp_path / "caps", out=out, ask=lambda _: answer,
                             client_factory=lambda: client)
    return code, client, out.getvalue()


def test_decline_sends_nothing(cfg, tmp_path):
    code, client, out = run(cfg, tmp_path, "decisions-luna", "n")
    assert code == 0 and client.calls == []
    assert "USD" in out and "Anulowano" in out
    assert not (tmp_path / "caps").exists()


@pytest.mark.parametrize("kind,path,model", [
    ("decisions-luna", "/api/alpha/decisions", "openai/gpt-6-luna-decisions"),
    ("decisions-jev", "/api/alpha/decisions", "typesafe/jev-1.14"),
    ("chat-tier2", "/api/v1/chat/completions", "openai/gpt-6-luna"),
])
def test_accept_sends_exactly_one_and_writes_capture(cfg, tmp_path, kind, path, model):
    code, client, out = run(cfg, tmp_path, kind, "y")
    assert code == 0 and client.calls == [(path, model)]
    files = list((tmp_path / "caps").glob("*.json"))
    assert len(files) == 1 and files[0].name.startswith(kind)


def test_sign_crop_image_selected_by_id(cfg, tmp_path):
    code, client, out = run(cfg, tmp_path, "decisions-luna", "y", image="mapillary_1931009810597411")
    assert code == 0 and len(client.calls) == 1
    assert list((tmp_path / "caps").glob("decisions-luna-sign_crop-*.json"))


def test_missing_key_exit_3(cfg, tmp_path):
    from map_qa.core.errors import MissingCredential
    with pytest.raises(MissingCredential):
        run_model_capture(cfg, {}, kind="decisions-luna", yes=True, image=None, name=None,
                          captures_dir=tmp_path / "c", out=io.StringIO(), ask=lambda _: "y")
