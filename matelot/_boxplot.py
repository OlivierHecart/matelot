"""
matelot._boxplot
----------------
A brightness-aware wrapper around seaborn.boxplot.
"""
from __future__ import annotations

from typing import Any

import pandas as pd
import seaborn as sns

from matelot._core import ColumnName, _Vector, prepare_brightness


def boxplot(
    data: pd.DataFrame | None = None,
    *,
    x: ColumnName | _Vector | None = None,
    y: ColumnName | _Vector | None = None,
    hue: ColumnName | _Vector | None = None,
    order: list[Any] | None = None,
    hue_order: list[Any] | None = None,
    orient: str | None = None,
    color: Any = None,
    palette: Any = None,
    saturation: float = 0.75,
    fill: bool = True,
    dodge: Any = "auto",
    width: float = 0.8,
    gap: float = 0,
    whis: float = 1.5,
    linecolor: Any = "auto",
    linewidth: float | None = None,
    fliersize: float | None = None,
    hue_norm: Any = None,
    native_scale: bool = False,
    log_scale: Any = None,
    formatter: Any = None,
    legend: str = "auto",
    ax: Any = None,
    brightness: ColumnName | _Vector | None = None,
    **kwargs: Any,
) -> Any:
    """
    seaborn.boxplot extended with a `brightness` argument.

    Parameters
    ----------
    brightness : column name or array-like, optional
        A column whose unique values drive lightness shading within each `hue`
        group. When provided, `hue` must also be given.

    Raises
    ------
    TypeError
        If `data` is not a pandas DataFrame.
    ValueError
        If `brightness` is provided but `hue` is not.
    """
    if brightness is None:
        return sns.boxplot(
            data=data,
            x=x, y=y,
            hue=hue, order=order, hue_order=hue_order,
            orient=orient, color=color, palette=palette,
            saturation=saturation, fill=fill, dodge=dodge,
            width=width, gap=gap, whis=whis,
            linecolor=linecolor, linewidth=linewidth, fliersize=fliersize,
            hue_norm=hue_norm, native_scale=native_scale, log_scale=log_scale,
            formatter=formatter, legend=legend, ax=ax,
            **kwargs,
        )

    df, combined_palette, combined_hue_order = prepare_brightness(
        data, hue, brightness, palette, hue_order, "boxplot"
    )

    return sns.boxplot(
        data=df,
        x=x, y=y,
        hue="_matelot_combined",
        order=order,
        hue_order=combined_hue_order,
        orient=orient, color=color, palette=combined_palette,
        saturation=saturation, fill=fill, dodge=dodge,
        width=width, gap=gap, whis=whis,
        linecolor=linecolor, linewidth=linewidth, fliersize=fliersize,
        hue_norm=hue_norm, native_scale=native_scale, log_scale=log_scale,
        formatter=formatter, legend=legend, ax=ax,
        **kwargs,
    )
