import pytest
from pathlib import Path
from envdrift.templater import collect_keys, build_example, render_example, write_example
from envdrift.template_commands import cmd_template
import argparse


@pytest.fixture
def tmp_env(tmp_path):
    def _write(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_collect_keys_order():
    envs = [{"A": "1", "B": "2"}, {"B": "x", "C": "3"}]
    assert collect_keys(envs) == ["A", "B", "C"]


def test_build_example_sensitive_keys_blanked():
    envs = [{"SECRET_KEY": "abc123", "PORT": "8080"}]
    result = build_example(envs, placeholder="REDACTED")
    assert result["SECRET_KEY"] == "REDACTED"
    assert result["PORT"] == "8080"


def test_build_example_keep_safe_false():
    envs = [{"PORT": "8080", "HOST": "localhost"}]
    result = build_example(envs, placeholder="", keep_safe_values=False)
    assert result["PORT"] == ""
    assert result["HOST"] == ""


def test_build_example_first_value_wins():
    envs = [{"PORT": "8080"}, {"PORT": "9090"}]
    result = build_example(envs)
    assert result["PORT"] == "8080"


def test_render_example_format():
    example = {"A": "1", "B": ""}
    text = render_example(example)
    assert "A=1" in text
    assert "B=" in text
    assert text.endswith("\n")


def test_render_example_empty():
    assert render_example({}) == ""


def test_write_example_creates_file(tmp_path):
    envs = [{"DB_PASSWORD": "secret", "PORT": "5432"}]
    out = tmp_path / ".env.example"
    write_example(envs, out, placeholder="")
    content = out.read_text()
    assert "PORT=5432" in content
    assert "DB_PASSWORD=" in content


def test_cmd_template_stdout(tmp_env, capsys):
    p = tmp_env("dev.env", "PORT=8080\nSECRET=abc\n")
    ns = argparse.Namespace(envfiles=[p], output=None, placeholder="", blank_safe=False)
    rc = cmd_template(ns)
    assert rc == 0
    out = capsys.readouterr().out
    assert "PORT=" in out


def test_cmd_template_missing_file(tmp_path):
    ns = argparse.Namespace(
        envfiles=[str(tmp_path / "missing.env")],
        output=None, placeholder="", blank_safe=False,
    )
    assert cmd_template(ns) == 1


def test_cmd_template_output_file(tmp_env, tmp_path):
    p = tmp_env("prod.env", "API_KEY=xyz\nHOST=prod.example.com\n")
    out = str(tmp_path / "out.env")
    ns = argparse.Namespace(envfiles=[p], output=out, placeholder="CHANGE_ME", blank_safe=False)
    rc = cmd_template(ns)
    assert rc == 0
    content = Path(out).read_text()
    assert "API_KEY=CHANGE_ME" in content
    assert "HOST=prod.example.com" in content
