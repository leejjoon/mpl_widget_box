import numpy as np
from matplotlib.offsetbox import DrawingArea
import matplotlib.lines as mlines

from astropy.visualization import (
    LinearStretch,
    LogStretch,
    SqrtStretch,
    SquaredStretch,
    AsinhStretch,
    ImageNormalize,
)


def norm_from_stretch(stretch):
    def _norm():
        return ImageNormalize(stretch=stretch())

    return _norm


def get_norms():
    _norms = [
        ("linear", LinearStretch),
        ("log", LogStretch),
        ("sqrt", SqrtStretch),
        ("squared", SquaredStretch),
        ("asinh", AsinhStretch),
    ]

    norms = dict((k, norm_from_stretch(stretch=s)) for k, s in _norms)

    return norms


Norms = get_norms()


def get_norm_da(norm_name, w=10, h=10):
    da = DrawingArea(w, h, 0, 0)

    a = np.linspace(0, 1, w)
    l = mlines.Line2D(a * w, Norms[norm_name]()(a) * h, lw=3, color="0.5")
    da.add_artist(l)

    return da
