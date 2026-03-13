import pandas as pd
import pytest

import matelot


@pytest.fixture()
def simple_df():
    return pd.DataFrame({
        "x": ["A", "A", "A", "A", "B", "B", "B", "B"] * 3,
        "y": [1, 2, 3, 4, 5, 6, 7, 8] * 3,
        "group": (["G1"] * 4 + ["G1"] * 4) * 3,
        "level": (["low"] * 2 + ["high"] * 2 + ["low"] * 2 + ["high"] * 2) * 3,
    })


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def test_raises_typeerror_for_non_dataframe():
    with pytest.raises(TypeError, match="pandas DataFrame"):
        matelot.boxplot(data={"x": ["A"], "y": [1]}, x="x", y="y",
                        hue="group", brightness="level")


def test_raises_valueerror_when_brightness_without_hue(simple_df):
    with pytest.raises(ValueError, match="hue"):
        matelot.boxplot(data=simple_df, x="x", y="y", brightness="level")


# ---------------------------------------------------------------------------
# Combined column construction
# ---------------------------------------------------------------------------

def test_combined_column_values(simple_df, monkeypatch):
    calls = []
    import seaborn as sns
    monkeypatch.setattr(sns, "boxplot", lambda **kw: calls.append(kw) or None)

    matelot.boxplot(data=simple_df, x="x", y="y", hue="group", brightness="level")

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
    with mock.patch.object(sns, "boxplot"):
        matelot.boxplot(data=simple_df, x="x", y="y", hue="group", brightness="level")
    assert set(simple_df.columns) == original_cols


# ---------------------------------------------------------------------------
# hue_order rewriting
# ---------------------------------------------------------------------------

def test_hue_order_forwarded_as_combined(simple_df, monkeypatch):
    import seaborn as sns
    calls = []
    monkeypatch.setattr(sns, "boxplot", lambda **kw: calls.append(kw) or None)

    matelot.boxplot(data=simple_df, x="x", y="y",
                    hue="group", brightness="level", hue_order=["G1"])

    hue_order_passed = calls[0]["hue_order"]
    assert all(" " in v for v in hue_order_passed)


# ---------------------------------------------------------------------------
# Passthrough path (no brightness)
# ---------------------------------------------------------------------------

def test_passthrough_no_brightness(simple_df, monkeypatch):
    import seaborn as sns
    calls = []
    monkeypatch.setattr(sns, "boxplot", lambda **kw: calls.append(kw) or None)

    matelot.boxplot(data=simple_df, x="x", y="y", hue="group")

    assert calls[0]["hue"] == "group"


# ---------------------------------------------------------------------------
# boxplot-specific arguments are forwarded
# ---------------------------------------------------------------------------

def test_boxplot_specific_args_forwarded(simple_df, monkeypatch):
    import seaborn as sns
    calls = []
    monkeypatch.setattr(sns, "boxplot", lambda **kw: calls.append(kw) or None)

    matelot.boxplot(data=simple_df, x="x", y="y", hue="group", brightness="level",
                    whis=2.0, width=0.5, saturation=0.5)

    assert calls[0]["whis"] == 2.0
    assert calls[0]["width"] == 0.5
    assert calls[0]["saturation"] == 0.5
