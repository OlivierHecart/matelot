import io
import xml.etree.ElementTree as ET

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import pytest

import matelot
from matelot._svg import InteractiveFigure, interactive, _save_interactive_svg


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


@pytest.fixture()
def simple_df():
    return pd.DataFrame({
        "x": [1, 2, 3, 1, 2, 3],
        "y": [1.0, 4.0, 9.0, 2.0, 5.0, 8.0],
        "group": ["A", "A", "A", "B", "B", "B"],
    })


def _get_matelot_line_gids(ax):
    return [
        line.get_gid() for line in ax.get_lines()
        if line.get_gid() and line.get_gid().startswith("_matelot_line_")
    ]


def _get_tooltip_gids(ax):
    return [
        child.get_gid() for child in ax.get_children()
        if hasattr(child, "get_gid") and child.get_gid()
        and child.get_gid().startswith("_matelot_tooltip_")
    ]


def _get_annotation_texts(ax):
    import matplotlib.text as mtext
    return [c for c in ax.get_children() if isinstance(c, mtext.Annotation)]


# ---------------------------------------------------------------------------
# annotate="interactive"
# ---------------------------------------------------------------------------

def test_interactive_sets_line_gids(simple_df):
    fig, ax = plt.subplots()
    matelot.lineplot(data=simple_df, x="x", y="y", hue="group", ax=ax, annotate="interactive")
    gids = _get_matelot_line_gids(ax)
    assert len(gids) > 0


def test_interactive_adds_tooltip_gids(simple_df):
    fig, ax = plt.subplots()
    matelot.lineplot(data=simple_df, x="x", y="y", hue="group", ax=ax, annotate="interactive")
    assert len(_get_tooltip_gids(ax)) > 0


def test_interactive_gid_format_matches(simple_df):
    fig, ax = plt.subplots()
    matelot.lineplot(data=simple_df, x="x", y="y", hue="group", ax=ax, annotate="interactive")
    line_gids = set(_get_matelot_line_gids(ax))
    for tgid in _get_tooltip_gids(ax):
        base = "_matelot_line_" + "_".join(tgid.replace("_matelot_tooltip_", "").rsplit("_", 1)[:-1])
        assert any(lgid.startswith(base) for lgid in line_gids), (
            f"No matching line GID for tooltip {tgid!r}"
        )


def test_interactive_uids_differ_across_calls(simple_df):
    fig, ax = plt.subplots()
    matelot.lineplot(data=simple_df, x="x", y="y", hue="group", ax=ax, annotate="interactive")
    matelot.lineplot(data=simple_df, x="x", y="y", hue="group", ax=ax, annotate="interactive")
    all_gids = _get_matelot_line_gids(ax)
    uids = {gid.split("_")[3] for gid in all_gids}
    assert len(uids) == 2


# ---------------------------------------------------------------------------
# annotate="static"
# ---------------------------------------------------------------------------

def test_static_adds_annotations(simple_df):
    fig, ax = plt.subplots()
    matelot.lineplot(data=simple_df, x="x", y="y", hue="group", ax=ax, annotate="static")
    assert len(_get_annotation_texts(ax)) > 0


def test_static_no_matelot_gids(simple_df):
    fig, ax = plt.subplots()
    matelot.lineplot(data=simple_df, x="x", y="y", hue="group", ax=ax, annotate="static")
    assert _get_matelot_line_gids(ax) == []
    assert _get_tooltip_gids(ax) == []


# ---------------------------------------------------------------------------
# bool / None aliases
# ---------------------------------------------------------------------------

def test_true_is_alias_for_static(simple_df):
    fig, ax = plt.subplots()
    matelot.lineplot(data=simple_df, x="x", y="y", hue="group", ax=ax, annotate=True)
    assert len(_get_annotation_texts(ax)) > 0
    assert _get_matelot_line_gids(ax) == []


def test_false_produces_no_annotations(simple_df):
    fig, ax = plt.subplots()
    matelot.lineplot(data=simple_df, x="x", y="y", hue="group", ax=ax, annotate=False)
    assert _get_annotation_texts(ax) == []
    assert _get_matelot_line_gids(ax) == []


def test_none_produces_no_annotations(simple_df):
    fig, ax = plt.subplots()
    matelot.lineplot(data=simple_df, x="x", y="y", hue="group", ax=ax, annotate=None)
    assert _get_annotation_texts(ax) == []
    assert _get_matelot_line_gids(ax) == []


# ---------------------------------------------------------------------------
# InteractiveFigure / interactive
# ---------------------------------------------------------------------------

def test_interactive_returns_interactive_figure(simple_df):
    fig, ax = plt.subplots()
    matelot.lineplot(data=simple_df, x="x", y="y", hue="group", ax=ax, annotate="interactive")
    af = matelot.interactive(fig)
    assert isinstance(af, InteractiveFigure)


def test_interactive_figure_savefig_produces_svg(simple_df, tmp_path):
    fig, ax = plt.subplots()
    matelot.lineplot(data=simple_df, x="x", y="y", hue="group", ax=ax, annotate="interactive")
    af = matelot.interactive(fig)
    out = tmp_path / "out.svg"
    af.savefig(str(out))
    content = out.read_bytes()
    assert b"<svg" in content
    assert b"ShowTooltip" in content
    assert b"HideTooltip" in content


# ---------------------------------------------------------------------------
# Module-level savefig
# ---------------------------------------------------------------------------

def test_module_savefig_uses_gcf(simple_df, tmp_path):
    fig, ax = plt.subplots()
    matelot.lineplot(data=simple_df, x="x", y="y", hue="group", ax=ax, annotate="interactive")
    # fig is now gcf
    out = tmp_path / "out.svg"
    matelot.savefig(str(out))
    content = out.read_bytes()
    assert b"<svg" in content
    assert b"ShowTooltip" in content


# ---------------------------------------------------------------------------
# SVG structure
# ---------------------------------------------------------------------------

def test_svg_tooltips_hidden(simple_df, tmp_path):
    fig, ax = plt.subplots()
    matelot.lineplot(data=simple_df, x="x", y="y", hue="group", ax=ax, annotate="interactive")
    out = tmp_path / "out.svg"
    _save_interactive_svg(fig, str(out))

    content = out.read_bytes()
    _, xmlid = ET.XMLID(content)

    tooltip_elems = {k: v for k, v in xmlid.items() if k.startswith("_matelot_tooltip_")}
    assert len(tooltip_elems) > 0
    for elem in tooltip_elems.values():
        assert elem.get("visibility") == "hidden"


def test_svg_lines_have_mouse_events(simple_df, tmp_path):
    fig, ax = plt.subplots()
    matelot.lineplot(data=simple_df, x="x", y="y", hue="group", ax=ax, annotate="interactive")
    out = tmp_path / "out.svg"
    _save_interactive_svg(fig, str(out))

    content = out.read_bytes()
    _, xmlid = ET.XMLID(content)

    line_elems = {k: v for k, v in xmlid.items() if k.startswith("_matelot_line_")}
    assert len(line_elems) > 0
    for elem in line_elems.values():
        assert "ShowTooltip" in elem.get("onmouseover", "")
        assert "HideTooltip" in elem.get("onmouseout", "")


def test_svg_format_kwarg_ignored(simple_df, tmp_path):
    fig, ax = plt.subplots()
    matelot.lineplot(data=simple_df, x="x", y="y", hue="group", ax=ax, annotate="interactive")
    out = tmp_path / "out.svg"
    # Should not raise even if format is passed
    _save_interactive_svg(fig, str(out), format="png")
    assert b"<svg" in out.read_bytes()
