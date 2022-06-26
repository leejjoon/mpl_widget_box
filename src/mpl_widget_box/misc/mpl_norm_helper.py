import numpy as np
import matplotlib.colors as mcolors

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


if __name__ == "__main__":

    Norms = get_norms()

    arr = np.arange(100).reshape((10, 10))

    fig, ax = plt.subplots(1, 1, num=1, clear=True)
    im = ax.imshow(arr)

    a = np.linspace(0, 1, 100)

    im.set_norm(Norms["sqrt"]())

    clf()
    ax = plt.axes([0.1, 0.1, 0.2, 0.2])
    ax.plot(a, Norms["log"]()(a), lw=4, c="0.5")

from matplotlib.offsetbox import DrawingArea
import matplotlib.lines as mlines

Norms = get_norms()


def get_norm_da(norm_name, w=10, h=10):
    da = DrawingArea(w, h, 0, 0)

    a = np.linspace(0, 1, w)
    l = mlines.Line2D(a * w, Norms[norm_name]()(a) * h, lw=3, color="0.5")
    da.add_artist(l)

    return da


if False:
    from matplotlib.offsetbox import (
        OffsetBox,
        AnnotationBbox,
        DrawingArea,
        TextArea,
        OffsetImage,
    )

    fig, ax = plt.subplots(1, 1, num=1, clear=True)

    da = get_norm_da("asinh")
    xy = (0.5, 0.5)
    xybox = (0, 0)
    box = AnnotationBbox(
        da,
        xy=xy,
        xybox=xybox,
        boxcoords="offset points",
        # box_alignment=(0, 1),
        pad=0.3,
        animated=False,
    )
    ax.add_artist(box)
