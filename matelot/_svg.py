"""
matelot._svg
------------
SVG animation helpers: InteractiveFigure, interactive, and module-level savefig.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from io import BytesIO
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

ET.register_namespace("", "http://www.w3.org/2000/svg")

_SCRIPT = """<script type="text/ecmascript">
<![CDATA[

function init(event) {
    if ( window.svgDocument == null ) {
        svgDocument = event.target.ownerDocument;
        }
    }

function ShowTooltip(id) {
    for (const el of svgDocument.getElementsByTagName('*')) {
        if (el.id.startsWith(id)) {
            el.setAttribute('visibility', "visible")
        }
    }
}

function HideTooltip(id) {
    for (const el of svgDocument.getElementsByTagName('*')) {
        if (el.id.startsWith(id)) {
            el.setAttribute('visibility', "hidden")
        }
    }
}

]]>
</script>"""


def _save_interactive_svg(figure: Figure, fname: Any, **kwargs: Any) -> None:
    kwargs.pop("format", None)

    f = BytesIO()
    figure.savefig(f, format="svg", **kwargs)

    tree, xmlid = ET.XMLID(f.getvalue())
    tree.set("onload", "init(event)")

    for id_, elem in xmlid.items():
        if id_.startswith("_matelot_tooltip_"):
            elem.set("visibility", "hidden")
        if id_.startswith("_matelot_line_"):
            tooltip_id = id_.replace("_matelot_line_", "_matelot_tooltip_")
            elem.set("onmouseover", f"ShowTooltip('{tooltip_id}')")
            elem.set("onmouseout", f"HideTooltip('{tooltip_id}')")

    tree.insert(0, ET.XML(_SCRIPT))
    ET.ElementTree(tree).write(fname)


class InteractiveFigure:
    def __init__(self, figure: Figure) -> None:
        self._figure = figure

    def savefig(self, fname: Any, **kwargs: Any) -> None:
        _save_interactive_svg(self._figure, fname, **kwargs)


def interactive(figure: Figure) -> InteractiveFigure:
    return InteractiveFigure(figure)


def savefig(fname: Any, **kwargs: Any) -> None:
    _save_interactive_svg(plt.gcf(), fname, **kwargs)
