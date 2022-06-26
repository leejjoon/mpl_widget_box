import numpy as np
from matplotlib import rcParams
from matplotlib.offsetbox import (
    TextArea,
    DrawingArea,
)
from matplotlib.image import BboxImage

from .. import (widgets as W,
                WidgetBoxManager)
from ..composite_widget import CompositeWidget
from .matplotlib_colormaps import get_matplotlib_cmaps

try:
    from .mpl_norm_helper import get_norm_da, get_norms
    include_norm_buttons = True
except ImportError:
    print("no norm support")
    include_norm_buttons = False


def get_colorbar(gradient, cmap, width, height):
    da = DrawingArea(width, height, 0, 0)
    image = BboxImage(
        bbox=da.get_window_extent,
        cmap=cmap,
    )
    image.set_data(gradient)
    da.add_artist(image)

    return da, image


def get_colormap(cmap):
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    da, _ = get_colorbar(gradient, cmap, 80, 10)

    t = TextArea(cmap)
    p = W.HPacker(pad=0, sep=6, children=[da, t])

    return p


def get_colormap_widgets(cmaps, kind):
    sub_widgets = [get_colormap(cmap) for cmap in cmaps[kind][1]]

    return sub_widgets, cmaps[kind][1]


class CbarSelectorWidget(CompositeWidget):
    def _prefixed_name(self, n):
        return f"{self.rootname}:{n}"

    def __init__(self, rootname):
        self.rootname = rootname

        self.cmaps = get_matplotlib_cmaps()
        self.cm_kind_list = list(self.cmaps.keys())
        _gradient = np.linspace(0, 1, 256)
        self.gradient = np.vstack((_gradient, _gradient))

        if include_norm_buttons:
            self.norms = get_norms()
        else:
            self.norms = {}

        # use the default cm name. This will be updated later.
        cm_name = rcParams["image.cmap"]
        self.cbar, self.cbar_im = get_colorbar(self.gradient, cm_name, 80, 10)

    def update_cbar_widget(self, wbm, selected_name):

        self.cbar_im.set_cmap(selected_name)

        cm_name = wbm.get_widget_by_id(self._prefixed_name("cm-name"))
        cm_name.set_label(selected_name)

    def update_kind(self, wbm, kind):
        cm_widgets, cm_names = get_colormap_widgets(self.cmaps, kind)

        cmap_menu_items = wbm.get_widget_by_id(
            self._prefixed_name("cm-selector")
        )

        cmap_menu_items.replace_labels(cm_widgets, values=cm_names)

    def build_widgets(self):

        cm_widgets, cm_names = get_colormap_widgets(self.cmaps, "perceptual")

        sub_widgets = [
            W.HWidgets(
                [
                    W.Label(self._prefixed_name("cm-kind-label"), "kind"),
                    W.Dropdown(self._prefixed_name("cm-kind"), "",
                               self.cm_kind_list),
                ]
            ),
            W.DropdownMenu(self._prefixed_name("cm-selector"),
                           cm_widgets, values=cm_names),
        ]

        if include_norm_buttons:

            norm_names = ["linear", "sqrt", "log", "squared"]
            _norm_da = [get_norm_da(c) for c in norm_names]
            norm_buttons = [W.ButtonBar(self._prefixed_name("norm-selector"),
                                       _norm_da,
                                       values=norm_names, tooltips=norm_names)]
        else:
            norm_buttons = []

        widgets = [W.Sub(self._prefixed_name("sub"), self.cbar, sub_widgets, where="parent",
                         tooltip="select colorbar"),
                   W.Label(self._prefixed_name("cm-name"), ""), ]

        return widgets + norm_buttons

    def post_install(self, wbm):
        pass

    def post_uninstall(self, wbm):
        pass

    def process_event(self,
                      wbm: WidgetBoxManager, ev: W.WidgetBoxEvent, status,
                      im):
        # when colormap button is selected.
        if ev.wid == self._prefixed_name("cm-selector"):
            selected_cmap = status[self._prefixed_name("cm-selector")]["value"]
            self.update_cbar_widget(wbm, selected_cmap)
            im.set_cmap(selected_cmap)

            wbm.draw_idle()
            return True
        # when cm-kind dropdown menu is selected
        elif ev.wid == self._prefixed_name("cm-kind:select"):
            kind = status[self._prefixed_name("cm-kind")]["value"]
            self.update_kind(wbm, kind)
            return True

        # when norm is selected
        elif ev.wid == self._prefixed_name("norm-selector"):
            norm_name = status[self._prefixed_name("norm-selector")]["value"]
            im.set_norm(self.norms[norm_name]())
            self.cbar_im.set_norm(self.norms[norm_name]())

            wbm.draw_idle()
            return True
