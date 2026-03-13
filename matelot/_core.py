"""
matelot._core
-------------
Shared logic for brightness-aware palette generation and data preparation.
"""
from __future__ import annotations

import colorsys
import itertools
from typing import Any

import pandas as pd
import seaborn as sns

ColumnName = str
_Vector = Any


def _resolve_base_palette(
    palette: Any, n_hues: int
) -> list[tuple[float, float, float]]:
    if palette is not None:
        colors = sns.color_palette(palette, n_colors=n_hues)
    else:
        colors = sns.color_palette(n_colors=n_hues)
    return list(colors)


def _generate_shades(
    base_rgb: tuple[float, float, float],
    brightness_values: list[Any],
) -> dict[Any, tuple[float, float, float]]:
    n = len(brightness_values)
    r, g, b = base_rgb
    h, base_l, s = colorsys.rgb_to_hls(r, g, b)

    STEP = 0.1
    MIN_L = 0.0
    MAX_L = 0.8

    lightness_values = [base_l]
    left_mult = 1
    right_mult = 1
    turn = "left"

    while len(lightness_values) < n:
        if turn == "left":
            lightness_values.insert(0, max(MIN_L, base_l - STEP * left_mult))
            left_mult += 1
            turn = "right"
        else:
            lightness_values.append(min(MAX_L, base_l + STEP * right_mult))
            right_mult += 1
            turn = "left"

    sorted_bv = sorted(brightness_values, key=lambda x: str(x))

    return {
        bv: colorsys.hls_to_rgb(h, l, s)
        for bv, l in zip(sorted_bv, lightness_values)
    }


def _build_combined_palette(
    hue_values: list[Any],
    brightness_values: list[Any],
    base_palette_colors: list[tuple[float, float, float]],
) -> dict[str, tuple[float, float, float]]:
    color_cycle = itertools.cycle(base_palette_colors)
    palette: dict[str, tuple[float, float, float]] = {}

    for hue_val in hue_values:
        base_color = next(color_cycle)
        shades = _generate_shades(base_color, brightness_values)
        for bv, rgb in shades.items():
            palette[f"{hue_val} {bv}"] = rgb

    return palette


def _rewrite_hue_order(
    hue_order: list[Any],
    brightness_values: list[Any],
) -> list[str]:
    sorted_bv = sorted(brightness_values, key=lambda x: str(x))
    combined_order: list[str] = []
    for hue_val in hue_order:
        for bv in sorted_bv:
            combined_order.append(f"{hue_val} {bv}")
    return combined_order


def prepare_brightness(
    data: pd.DataFrame,
    hue: ColumnName,
    brightness: ColumnName,
    palette: Any,
    hue_order: list[Any] | None,
    func_name: str,
) -> tuple[pd.DataFrame, dict[str, Any], list[str] | None]:
    """
    Validate inputs, build the combined column and palette.

    Returns the extended DataFrame, the combined palette dict, and the
    rewritten hue_order (or None).

    Raises
    ------
    TypeError
        If `data` is not a pd.DataFrame.
    ValueError
        If `brightness` is provided but `hue` is not.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError(
            f"matelot.{func_name} requires `data` to be a pandas DataFrame. "
            f"Got {type(data).__name__!r} instead. "
            "Seaborn's broader input types (dicts, etc.) are not supported."
        )

    if hue is None:
        raise ValueError(
            f"matelot.{func_name}: `brightness` was provided but `hue` is None. "
            "`hue` must be specified whenever `brightness` is used."
        )

    df = data.copy()
    df["_matelot_combined"] = df.apply(
        lambda row: str(row[hue]) + " " + str(row[brightness]), axis=1
    )

    unique_hue_vals: list[Any] = list(dict.fromkeys(df[hue]))
    unique_brightness_vals: list[Any] = list(dict.fromkeys(df[brightness]))

    base_colors = _resolve_base_palette(palette, len(unique_hue_vals))
    combined_palette = _build_combined_palette(
        unique_hue_vals, unique_brightness_vals, base_colors
    )

    combined_hue_order: list[str] | None = None
    if hue_order is not None:
        combined_hue_order = _rewrite_hue_order(hue_order, unique_brightness_vals)

    return df, combined_palette, combined_hue_order
