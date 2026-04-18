import pytest
from pathlib import Path
from envdrift.pinner import (
    save_pins, load_pins, list_pins, check_pins, PinViolation, pins_path
)


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    import envdrift.pinner as pinner_mod
    pinner_mod.PINS_DIR = tmp_path / "pins"
    yield
    pinner_mod.PINS_DIR = Path(".envdrift") / "pins"


def test_save_creates_file(tmp_path, monkeypatch):
    import envdrift.pinner as m
    save_pins("prod", {"APP_ENV": "production"})
    assert m.PINS_DIR.joinpath("prod.json").exists()


def test_save_and_load_roundtrip():
    pins = {"APP_ENV": "production", "DEBUG": "false"}
    save_pins("prod", pins)
    loaded = load_pins("prod")
    assert loaded == pins


def test_load_missing_raises():
    with pytest.raises(FileNotFoundError):
        load_pins("nonexistent")


def test_list_pins_empty():
    assert list_pins() == []


def test_list_pins_returns_names():
    save_pins("alpha", {})
    save_pins("beta", {})
    assert list_pins() == ["alpha", "beta"]


def test_check_pins_no_violations():
    save_pins("prod", {"APP_ENV": "production"})
    result = check_pins("prod", {"APP_ENV": "production"}, env_file=".env.prod")
    assert not result.has_violations()
    assert result.env_file == ".env.prod"


def test_check_pins_wrong_value():
    save_pins("prod", {"APP_ENV": "production"})
    result = check_pins("prod", {"APP_ENV": "staging"})
    assert result.has_violations()
    v = result.violations[0]
    assert v.key == "APP_ENV"
    assert v.expected == "production"
    assert v.actual == "staging"


def test_check_pins_missing_key():
    save_pins("prod", {"APP_ENV": "production"})
    result = check_pins("prod", {})
    assert result.has_violations()
    assert result.violations[0].actual is None


def test_check_pins_multiple_violations():
    save_pins("prod", {"A": "1", "B": "2", "C": "3"})
    result = check_pins("prod", {"A": "1", "B": "X"})
    keys = {v.key for v in result.violations}
    assert keys == {"B", "C"}
