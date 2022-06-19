from typing import Literal

from .widgets import get_icon_fontprop
import fontawesome

from matplotlib.offsetbox import (
    OffsetBox,
    AnnotationBbox,
    DrawingArea,
    TextArea,
    OffsetImage,
    # HPacker,
    # VPacker,
)


def get_fa_textarea(icon_name: str,
                    color="k",
                    size: int = 10,
                    family: Literal["regular", "solid"] = "solid",
                    ):

    fontprop = get_icon_fontprop(family=family,
                                 size=size)

    button = TextArea(fontawesome.icons[icon_name],
                      textprops=dict(fontproperties=fontprop,
                                      color=color))
    return button
