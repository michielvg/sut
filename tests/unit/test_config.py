import json
from pathlib import Path
from config import Config

# -------------------------
# Helpers
# -------------------------
def make_config(tmp_path: Path, content: str) -> Config:
    config_file = tmp_path / "config.json"
    config_file.write_text(content)
    return Config(str(config_file))

# -------------------------
# Tests
# -------------------------
def test_load_valid_config(tmp_path: Path):
    data = {"section": {"key": "value"}}
    cfg = make_config(tmp_path, json.dumps(data))

    assert cfg.data == data


def test_load_missing_file(tmp_path: Path, capsys):
    config_file = tmp_path / "missing.json"

    cfg = Config(str(config_file))

    captured = capsys.readouterr()
    assert "not found" in captured.out.lower()
    assert cfg.data == {}


def test_load_invalid_json(tmp_path: Path, capsys):
    cfg = make_config(tmp_path, "{ invalid json }")

    captured = capsys.readouterr()
    assert "failed to load" in captured.out.lower()
    assert cfg.data == {}


def test_load_empty_file(tmp_path: Path, capsys):
    cfg = make_config(tmp_path, "")

    captured = capsys.readouterr()
    assert "failed to load" in captured.out.lower()
    assert cfg.data == {}


def test_load_json_not_dict(tmp_path: Path, capsys):
    cfg = make_config(tmp_path, "[]")  # valid JSON, wrong type

    captured = capsys.readouterr()
    assert "json object" in captured.out.lower()
    assert cfg.data == {}


def test_load_path_is_directory(tmp_path, capsys):
    cfg = Config(str(tmp_path))  # passing a directory

    captured = capsys.readouterr()
    assert "not found" in captured.out.lower()
    assert cfg.data == {}


def test_load_permission_error(tmp_path, capsys):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"a": 1}')

    config_file.chmod(0o000)

    try:
        cfg = Config(str(config_file))

        captured = capsys.readouterr()
        assert "error" in captured.out.lower()
        assert cfg.data == {}
    finally:
        config_file.chmod(0o644)


def test_get_section_existing_dict(tmp_path: Path):
    cfg = make_config(tmp_path, json.dumps({"my_section": {"a": 1}}))

    assert cfg.get_section("my_section") == {"a": 1}


def test_get_section_missing(tmp_path: Path):
    cfg = make_config(tmp_path, json.dumps({}))

    assert cfg.get_section("unknown") is None


def test_get_section_null(tmp_path: Path):
    cfg = make_config(tmp_path, json.dumps({"my_section": None}))

    assert cfg.get_section("my_section") is None


def test_get_section_false(tmp_path: Path):
    cfg = make_config(tmp_path, json.dumps({"my_section": False}))

    assert cfg.get_section("my_section") is False


def test_null_section_behaves_like_missing(tmp_path):
    cfg = make_config(tmp_path, '{"feature": null}')

    assert cfg.get_section("feature") is None


def test_reload_overwrites_data(tmp_path):
    config_file = tmp_path / "config.json"
    config_file.write_text('{"a": 1}')

    cfg = Config(str(config_file))
    assert cfg.get_section("a") == 1

    config_file.write_text('{"b": 2}')
    cfg.load(str(config_file))

    assert cfg.get_section("a") is None
    assert cfg.get_section("b") == 2