"""Regler-Grenzen, Presets und Konstanten fuer die Doppel-K.-o.-Demo."""

N_SEEDS_OPTIONS = [4, 8, 16, 32]
DEFAULT_N_SEEDS = 8

DEFAULT_SEED = 1
SEED_MIN, SEED_MAX = 0, 999

FAVORITE_EDGE_MIN, FAVORITE_EDGE_MAX, FAVORITE_EDGE_STEP = 0, 800, 50
DEFAULT_FAVORITE_EDGE = 500

SWEEP_N_SEEDS_VALUES = [4, 8, 16, 32]
SWEEP_REPS = 3000

_BASE = {"n_seeds": DEFAULT_N_SEEDS, "seed": DEFAULT_SEED, "favorite_edge": DEFAULT_FAVORITE_EDGE}
PRESETS = {
    "Normalfall (8 Teams)": {**_BASE},
    "Doppelter Schutz sichtbar (16 Teams)": {**_BASE, "n_seeds": 16, "seed": 3},
    "Bracket-Reset erlebt (32 Teams)": {**_BASE, "n_seeds": 32, "seed": 1},
    "Ausgeglichenes Feld (kein Favorit)": {**_BASE, "favorite_edge": 0},
}
PRESET_HELP = {
    "Normalfall (8 Teams)": "8 Teams, deutlicher Favorit auf Setzplatz 1 - Standardgröße für den direkten Vergleich.",
    "Doppelter Schutz sichtbar (16 Teams)": "Bei 16 Teams zeigt sich der Effekt der zweiten Chance besonders deutlich in der Sieg-Wahrscheinlichkeit.",
    "Bracket-Reset erlebt (32 Teams)": "Bei diesem Zufalls-Seed gewinnt das Verlierer-Baum-Team das erste Finale - es kommt zum Bracket-Reset (zweites, entscheidendes Spiel).",
    "Ausgeglichenes Feld (kein Favorit)": "Alle Teams gleich stark - zeigt, dass der Doppel-K.-o.-Vorteil an einen ECHTEN Stärkeunterschied gebunden ist, nicht an die Setzliste allein.",
}
