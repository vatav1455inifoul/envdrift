import pytest
from pathlib import Path
from envdrift.annotator import annotate_env, write_annotated, AnnotatedLine


@pytest.fixture
def tmp_env(tmp_path):
    return tmp_path


def _write(p: Path, content: str):
    p.write_text(content)
    return str(p)


def test_no_drift_no_annotations(tmp_env):
    env = _write(tmp_env / "app.env", "KEY=value\nFOO=bar\n")
    ref = _write(tmp_env / "ref.env", "KEY=value\nFOO=bar\n")
    result = annotate_env(env, ref)
    for line in result.lines:
        assert line.annotation == ""


def test_extra_key_annotated(tmp_env):
    env = _write(tmp_env / "app.env", "KEY=value\nEXTRA=yes\n")
    ref = _write(tmp_env / "ref.env", "KEY=value\n")
    result = annotate_env(env, ref)
    extra = next(l for l in result.lines if l.key == "EXTRA")
    assert "EXTRA" in extra.annotation


def test_missing_key_annotated(tmp_env):
    env = _write(tmp_env / "app.env", "KEY=value\n")
    ref = _write(tmp_env / "ref.env", "KEY=value\nMISSING=x\n")
    result = annotate_env(env, ref)
    missing = next(l for l in result.lines if l.key == "MISSING")
    assert "MISSING" in missing.annotation


def test_changed_value_annotated(tmp_env):
    env = _write(tmp_env / "app.env", "KEY=new\n")
    ref = _write(tmp_env / "ref.env", "KEY=old\n")
    result = annotate_env(env, ref)
    changed = next(l for l in result.lines if l.key == "KEY")
    assert "CHANGED" in changed.annotation
    assert "old" in changed.annotation


def test_render_includes_annotation(tmp_env):
    env = _write(tmp_env / "app.env", "KEY=new\n")
    ref = _write(tmp_env / "ref.env", "KEY=old\n")
    result = annotate_env(env, ref)
    rendered = result.render()
    assert "[envdrift]" in rendered
    assert "CHANGED" in rendered


def test_write_annotated_creates_file(tmp_env):
    env = _write(tmp_env / "app.env", "KEY=value\n")
    ref = _write(tmp_env / "ref.env", "KEY=value\n")
    result = annotate_env(env, ref)
    out = str(tmp_env / "annotated.env")
    write_annotated(result, out)
    assert Path(out).exists()
    assert "KEY=value" in Path(out).read_text()


def test_env_name_stored(tmp_env):
    env = _write(tmp_env / "app.env", "K=v\n")
    ref = _write(tmp_env / "ref.env", "K=v\n")
    result = annotate_env(env, ref, env_name="staging")
    assert result.env_name == "staging"
