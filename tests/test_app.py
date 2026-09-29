"""Rauchtests der Streamlit-Oberflaeche per AppTest: Standard, jedes Preset, alle Teilnehmerzahlen,
Team-im-Fokus-Regler."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import de2_constants as C

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app.py"


def _run(setup=None):
    at = AppTest.from_file(str(APP), default_timeout=90)
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    if setup is not None:
        setup(at)
        at.run()
        assert not at.exception, [e.value for e in at.exception]
    return at


def test_default_renders_without_exception():
    at = _run()
    assert any("Doppel-K.-o." in t.value for t in at.title)


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_renders(name):
    p = C.PRESETS[name]

    def setup(at):
        at.session_state["n_seeds_select"] = p["n_seeds"]
        at.session_state["seed_slider"] = p["seed"]
        at.session_state["favorite_edge_slider"] = p["favorite_edge"]

    _run(setup)


@pytest.mark.parametrize("n_seeds", C.N_SEEDS_OPTIONS)
def test_every_n_seeds_renders(n_seeds):
    def setup(at):
        at.session_state["n_seeds_select"] = n_seeds

    _run(setup)


def test_focus_team_selectable():
    at = _run()
    at.session_state["focus_team_select"] = 2
    at.run()
    assert not at.exception


def test_favorite_edge_zero_renders():
    def setup(at):
        at.session_state["favorite_edge_slider"] = 0

    _run(setup)
