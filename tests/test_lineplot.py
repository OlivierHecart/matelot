import math
import pandas as pd
import pytest

import matelot
from matelot._core import (
    _generate_shades,
    _build_combined_palette,
    _rewrite_hue_order,
)


@pytest.fixture()
def simple_df():
    return pd.DataFrame({
        "x": [1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3],
        "y": [1, 2, 3, 4, 5, 6, 2, 3, 4, 5, 6, 7],
        "group": ["A", "A", "A", "A", "A", "A", "B", "B", "B", "B", "B", "B"],
        "level": ["low", "low", "low", "high", "high", "high",
                  "low", "low", "low", "high", "high", "high"],
    })


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def test_raises_typeerror_for_non_dataframe():
    with pytest.raises(TypeError, match="pandas DataFrame"):
        matelot.lineplot(data={"x": [1], "y": [1]}, x="x", y="y",
                         hue="group", brightness="level")


def test_raises_valueerror_when_brightness_without_hue(simple_df):
    with pytest.raises(ValueError, match="hue"):
        matelot.lineplot(data=simple_df, x="x", y="y", brightness="level")


# ---------------------------------------------------------------------------
# Combined column construction
# ---------------------------------------------------------------------------

def test_combined_column_values(simple_df, monkeypatch):
    calls = []
    import seaborn as sns
    monkeypatch.setattr(sns, "lineplot", lambda **kw: calls.append(kw) or None)

    matelot.lineplot(data=simple_df, x="x", y="y", hue="group", brightness="level")

    called_df = calls[0]["data"]
    assert "_matelot_combined" in called_df.columns
    expected = simple_df.apply(
        lambda r: str(r["level"]) + " " + str(r["group"]), axis=1
    )
    pd.testing.assert_series_equal(
        called_df["_matelot_combined"], expected, check_names=False
    )


def test_original_data_not_mutated(simple_df):
    original_cols = set(simple_df.columns)
    import seaborn as sns, unittest.mock as mock
    with mock.patch.object(sns, "lineplot"):
        matelot.lineplot(data=simple_df, x="x", y="y", hue="group", brightness="level")
    assert set(simple_df.columns) == original_cols


# ---------------------------------------------------------------------------
# Palette generation
# ---------------------------------------------------------------------------

def test_generate_shades_count():
    base = (0.2, 0.5, 0.8)
    shades = _generate_shades(base, ["low", "mid", "high"])
    assert len(shades) == 3
    assert set(shades.keys()) == {"low", "mid", "high"}


def test_generate_shades_lightness_ordering():
    import colorsys
    base = (0.2, 0.5, 0.8)
    shades = _generate_shades(base, ["z_high", "a_low"])
    l_a_low = colorsys.rgb_to_hls(*shades["a_low"])[1]
    l_z_high = colorsys.rgb_to_hls(*shades["z_high"])[1]
    assert l_a_low < l_z_high


def test_generate_shades_lightness_clamped():
    import colorsys
    # Near-black base: base-0.8 would go below 0.0 → clamped to 0.0
    base_dark = colorsys.hls_to_rgb(0.5, 0.05, 0.8)
    shades = _generate_shades(base_dark, ["a", "b", "c"])
    for rgb in shades.values():
        l = colorsys.rgb_to_hls(*rgb)[1]
        assert 0.0 <= l <= 0.8

    # Near-white base (≤ MAX_L): base+0.8 would exceed 0.8 → clamped to 0.8
    base_light = colorsys.hls_to_rgb(0.5, 0.75, 0.8)
    shades = _generate_shades(base_light, ["a", "b", "c"])
    for rgb in shades.values():
        l = colorsys.rgb_to_hls(*rgb)[1]
        assert 0.0 <= l <= 0.8


def test_generate_shades_pattern():
    """Verify the alternating left/right expansion pattern.

    STEP=0.1, base_l=0.5:
      n=1: [0.5]
      n=2: [0.4, 0.5]
      n=3: [0.4, 0.5, 0.6]
      n=4: [0.3, 0.4, 0.5, 0.6]
    """
    import colorsys
    base_l = 0.5
    base_rgb = colorsys.hls_to_rgb(0.0, base_l, 0.0)

    def get_l(rgb):
        return colorsys.rgb_to_hls(*rgb)[1]

    assert math.isclose(get_l(_generate_shades(base_rgb, ["a"])["a"]), base_l)

    l2 = sorted(get_l(v) for v in _generate_shades(base_rgb, ["a", "b"]).values())
    assert math.isclose(l2[0], 0.4) and math.isclose(l2[1], base_l)

    l3 = sorted(get_l(v) for v in _generate_shades(base_rgb, ["a", "b", "c"]).values())
    assert math.isclose(l3[0], 0.4)
    assert math.isclose(l3[1], base_l)
    assert math.isclose(l3[2], 0.6)

    l4 = sorted(get_l(v) for v in _generate_shades(base_rgb, ["a", "b", "c", "d"]).values())
    assert math.isclose(l4[0], 0.3)
    assert math.isclose(l4[1], 0.4)
    assert math.isclose(l4[2], base_l)
    assert math.isclose(l4[3], 0.6)


def test_generate_shades_single_value_uses_base_lightness():
    import colorsys
    base = (0.3, 0.6, 0.1)
    _, base_l, _ = colorsys.rgb_to_hls(*base)
    shades = _generate_shades(base, ["only"])
    result_l = colorsys.rgb_to_hls(*shades["only"])[1]
    assert math.isclose(result_l, base_l, abs_tol=1e-9)


def test_build_combined_palette_keys():
    palette = _build_combined_palette(["A", "B"], ["low", "high"],
                                      [(1.0, 0.0, 0.0), (0.0, 0.0, 1.0)])
    assert {"low A", "high A", "low B", "high B"} == set(palette.keys())


def test_build_combined_palette_cycles_colors():
    palette = _build_combined_palette(["A", "B", "C"], ["x"], [(1.0, 0.0, 0.0)])
    assert {"x A", "x B", "x C"} == set(palette.keys())


# ---------------------------------------------------------------------------
# hue_order rewriting
# ---------------------------------------------------------------------------

def test_rewrite_hue_order():
    result = _rewrite_hue_order(["B", "A"], ["high", "low"])
    assert result == ["high B", "low B", "high A", "low A"]


def test_hue_order_forwarded_as_combined(simple_df, monkeypatch):
    import seaborn as sns
    calls = []
    monkeypatch.setattr(sns, "lineplot", lambda **kw: calls.append(kw) or None)

    matelot.lineplot(data=simple_df, x="x", y="y",
                     hue="group", brightness="level", hue_order=["B", "A"])

    hue_order_passed = calls[0]["hue_order"]
    assert all(" " in v for v in hue_order_passed)


# ---------------------------------------------------------------------------
# Passthrough path (no brightness)
# ---------------------------------------------------------------------------

def test_passthrough_no_brightness(simple_df, monkeypatch):
    import seaborn as sns
    calls = []
    monkeypatch.setattr(sns, "lineplot", lambda **kw: calls.append(kw) or None)

    matelot.lineplot(data=simple_df, x="x", y="y", hue="group")

    assert calls[0]["hue"] == "group"
