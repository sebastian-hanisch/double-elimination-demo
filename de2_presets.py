"""SETTING_SPECS-Permalink-Muster (Standardmuster aus dem OR-Demo-Portfolio, s. drr_presets.py)."""

import math
from dataclasses import dataclass
from typing import Callable, Optional

import streamlit as st

import de2_constants as C


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: Callable
    default: object
    lo: Optional[float] = None
    hi: Optional[float] = None


def _n_seeds_caster(v):
    n = int(v)
    return n if n in C.N_SEEDS_OPTIONS else C.DEFAULT_N_SEEDS


SETTING_SPECS = {
    "n_seeds_select": SettingSpec("n", _n_seeds_caster, C.DEFAULT_N_SEEDS),
    "seed_slider": SettingSpec("seed", int, C.DEFAULT_SEED, C.SEED_MIN, C.SEED_MAX),
    "favorite_edge_slider": SettingSpec(
        "edge", int, C.DEFAULT_FAVORITE_EDGE, C.FAVORITE_EDGE_MIN, C.FAVORITE_EDGE_MAX
    ),
}


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def load_permalink_settings():
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            try:
                value = spec.caster(qp[spec.url_param])
                if isinstance(value, float) and not math.isfinite(value):
                    continue
                if spec.lo is not None:
                    value = max(spec.lo, value)
                if spec.hi is not None:
                    value = min(spec.hi, value)
                st.session_state[state_key] = value
            except (ValueError, TypeError):
                pass
    st.session_state["permalink_loaded"] = True


def sync_query_params(n_seeds, seed, favorite_edge):
    try:
        st.query_params["n"] = str(int(n_seeds))
        st.query_params["seed"] = str(int(seed))
        st.query_params["edge"] = str(int(favorite_edge))
    except Exception:
        pass


def apply_preset(name):
    p = C.PRESETS[name]
    st.session_state["n_seeds_select"] = p["n_seeds"]
    st.session_state["seed_slider"] = p["seed"]
    st.session_state["favorite_edge_slider"] = p["favorite_edge"]
