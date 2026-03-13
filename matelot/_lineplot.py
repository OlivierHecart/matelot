"""
matelot._lineplot
-----------------
A brightness-aware wrapper around seaborn.lineplot.
"""
from __future__ import annotations

from typing import Any

import pandas as pd
import seaborn as sns

from matelot._core import ColumnName, _Vector, prepare_brightness


def lineplot(
    data: pd.DataFrame | None = None,
    *,
    x: ColumnName | _Vector | None = None,
    y: ColumnName | _Vector | None = None,
    hue: ColumnName | _Vector | None = None,
    size: ColumnName | _Vector | None = None,
    style: ColumnName | _Vector | None = None,
    units: ColumnName | _Vector | None = None,
    weights: ColumnName | _Vector | None = None,
    palette: Any = None,
    hue_order: list[Any] | None = None,
    hue_norm: Any = None,
    sizes: Any = None,
    size_order: Any = None,
    size_norm: Any = None,
    dashes: Any = True,
    markers: Any = None,
    style_order: Any = None,
    estimator: Any = "mean",
    errorbar: Any = ("ci", 95),
    n_boot: int = 1000,
    seed: Any = None,
    orient: str = "x",
    sort: bool = True,
    err_style: str = "band",
    err_kws: dict[str, Any] | None = None,
    legend: str = "auto",
    ax: Any = None,
    brightness: ColumnName | _Vector | None = None,
    **kwargs: Any,
) -> Any:
    """
    seaborn.lineplot extended with a `brightness` argument.

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
        return sns.lineplot(
            data=data,
            x=x, y=y,
            hue=hue, size=size, style=style,
            units=units, weights=weights,
            palette=palette, hue_order=hue_order, hue_norm=hue_norm,
            sizes=sizes, size_order=size_order, size_norm=size_norm,
            dashes=dashes, markers=markers, style_order=style_order,
            estimator=estimator, errorbar=errorbar,
            n_boot=n_boot, seed=seed,
            orient=orient, sort=sort,
            err_style=err_style, err_kws=err_kws,
            legend=legend, ax=ax,
            **kwargs,
        )

    df, combined_palette, combined_hue_order = prepare_brightness(
        data, hue, brightness, palette, hue_order, "lineplot"
    )

    return sns.lineplot(
        data=df,
        x=x, y=y,
        hue="_matelot_combined",
        size=size, style=style,
        units=units, weights=weights,
        palette=combined_palette,
        hue_order=combined_hue_order,
        hue_norm=hue_norm,
        sizes=sizes, size_order=size_order, size_norm=size_norm,
        dashes=dashes, markers=markers, style_order=style_order,
        estimator=estimator, errorbar=errorbar,
        n_boot=n_boot, seed=seed,
        orient=orient, sort=sort,
        err_style=err_style, err_kws=err_kws,
        legend=legend, ax=ax,
        **kwargs,
    )
