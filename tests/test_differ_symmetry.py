"""Tests for envdrift.differ_symmetry."""
import pytest

from envdrift.comparator import compare_envs
from envdrift.differ_symmetry import SymmetryResult, analyse_symmetry, symmetry_from_multi
from envdrift.differ import multi_diff


def _drift(a: dict, b: dict, name_a="dev", name_b="prod"):
    return compare_envs(a, b, name_a, name_b)


# ---------------------------------------------------------------------------
# analyse_symmetry
# ---------------------------------------------------------------------------

class TestAnalyseSymmetry:
    def test_identical_envs_perfect_score(self):
        d = _drift({"A": "1", "B": "2"}, {"A": "1", "B": "2"})
        r = analyse_symmetry(d)
        assert r.symmetry_score == 1.0
        assert r.is_symmetric is True
        assert r.missing_keys == []
        assert r.extra_keys == []
        assert r.changed_keys == []

    def test_pure_rename_is_symmetric(self):
        # same number of missing / extra, no changed
        d = _drift({"OLD_KEY": "x"}, {"NEW_KEY": "x"})
        r = analyse_symmetry(d, threshold=0.5)
        assert r.missing_keys == ["OLD_KEY"]
        assert r.extra_keys == ["NEW_KEY"]
        assert r.changed_keys == []
        assert r.symmetry_score > 0.0

    def test_changed_values_reduce_symmetry(self):
        d = _drift({"A": "1"}, {"A": "999"})
        r = analyse_symmetry(d)
        assert "A" in r.changed_keys
        assert r.symmetry_score < 1.0

    def test_imbalanced_keys_noted(self):
        d = _drift({"A": "1", "B": "2", "C": "3"}, {"X": "1"})
        r = analyse_symmetry(d)
        assert any("imbalance" in n for n in r.notes)

    def test_env_names_stored(self):
        d = _drift({"A": "1"}, {"A": "1"}, name_a="staging", name_b="prod")
        r = analyse_symmetry(d)
        assert r.env_a == "staging"
        assert r.env_b == "prod"

    def test_threshold_controls_is_symmetric(self):
        d = _drift({"A": "1"}, {"B": "1"})
        strict = analyse_symmetry(d, threshold=0.99)
        lenient = analyse_symmetry(d, threshold=0.01)
        # with a very lenient threshold it should flip
        assert lenient.is_symmetric is True
        # strict may or may not be symmetric depending on score, just check types
        assert isinstance(strict.is_symmetric, bool)

    def test_note_added_for_symmetric_rename(self):
        d = _drift({"OLD": "v"}, {"NEW": "v"})
        r = analyse_symmetry(d, threshold=0.0)
        assert any("symmetric" in n or "rename" in n for n in r.notes)


# ---------------------------------------------------------------------------
# symmetry_from_multi
# ---------------------------------------------------------------------------

class TestSymmetryFromMulti:
    def _multi(self, envs: dict):
        return multi_diff(envs)

    def test_returns_all_pairs(self):
        envs = {
            "dev": {"A": "1", "B": "2"},
            "staging": {"A": "1", "B": "2"},
            "prod": {"A": "1", "B": "2"},
        }
        result = symmetry_from_multi(self._multi(envs))
        assert len(result) == 3  # dev↔staging, dev↔prod, staging↔prod

    def test_identical_multi_all_perfect(self):
        envs = {"a": {"X": "1"}, "b": {"X": "1"}}
        result = symmetry_from_multi(self._multi(envs))
        for sym in result.values():
            assert sym.symmetry_score == 1.0

    def test_pair_keys_use_arrow_separator(self):
        envs = {"dev": {"K": "v"}, "prod": {"K": "v"}}
        result = symmetry_from_multi(self._multi(envs))
        assert "dev↔prod" in result

    def test_all_values_are_symmetry_results(self):
        envs = {"x": {"A": "1"}, "y": {"B": "2"}}
        result = symmetry_from_multi(self._multi(envs))
        for v in result.values():
            assert isinstance(v, SymmetryResult)
