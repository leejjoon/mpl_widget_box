import numpy as np

import matplotlib.pyplot as plt
from matplotlib.offsetbox import (
    TextArea,
    DrawingArea,
    OffsetImage,
    AnnotationBbox,
    HPacker as _HPacker,
)
from matplotlib.image import BboxImage

from mpl_widget_box import WidgetBoxManager

# from guibox_widgets import Label, Button, Radio, Sub, Dropdown

from matplotlib_colormaps import get_matplotlib_cmaps

from widgets import (
    Sub,
    Label,
    Radio,
    Dropdown,
    HWidgets,
    DropdownMenu,
    HPacker,
    Button,
    ButtonBar,
    CheckBox,
    HWidgets,
)


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
    p = HPacker(pad=0, sep=6, children=[da, t])

    return p


def get_colormap_widgets(kind):
    sub_widgets = [get_colormap(cmap) for cmap in cmaps[kind][1]]

    return sub_widgets, cmaps[kind][1]


def select_cmap(im):
    pass


# def test_colorbar(cmaps=None):
if True:
    import matplotlib.pyplot as plt

    # plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Source Code Pro"]

    fig, ax = plt.subplots(num=2, clear=True)

    arr = np.arange(100).reshape((10, 10))
    im = ax.imshow(arr)

    wbm = WidgetBoxManager(fig)

    cmaps = get_matplotlib_cmaps()

    cm_kind_list = list(cmaps.keys())

    cm_widgets, cm_names = get_colormap_widgets("perceptual")

    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    cm_name = im.get_cmap().name
    cbar, cbar_im = get_colorbar(gradient, cm_name, 80, 10)

    sub_widgets = [
        HWidgets(
            children=[
                Label("cm-kind-label", "kind"),
                Dropdown("cm-kind", "", cm_kind_list),
            ]
        ),
        DropdownMenu("cm-selector", cm_widgets, values=cm_names),
    ]

    cmap_menu_items = sub_widgets[1]  # this will be used in the callback.

    from mpl_norm_helper import get_norm_da, get_norms

    norms = get_norms()

    norm_names = ["linear", "sqrt", "log", "squared"]
    _norm_da = [get_norm_da(c) for c in norm_names]

    widgets = [
        # HWidgets(children=[Button("btn1", "Xg", tooltip="close", pad=0, draw_frame=True)]),
        Button("btn1", "X", tooltip="close", pad=0, draw_frame=True, expand=False),
        Sub(
            "sub1",
            cbar,
            sub_widgets,
            # where="parent",
            tooltip="select colorbar",
        ),
        # Label("cm_name", cm_name),
        ButtonBar("norm-selector", _norm_da, values=norm_names, tooltips=norm_names),
        # Button("btn1", "Click", centered=True, tooltip="test"),
    ]
    # widgets.extend(cm_widgets)

    cm_name_label = widgets[1]

    # wbm.add_anchored_widget_box(widgets, ax)

    # wbm.add_anchored_widget_box(widgets, ax, loc=1)
    wbm.add_anchored_widget_box(widgets, ax, loc=1, dir="h")

    # wbm.add_anchored_widget_box(widgets, ax,
    #                             xy=(0, 1), xybox=(10, -10),
    #                             )

    def cb(wb, ev, status):
        draw_canvas = False

        # when colormap button is selected.
        if ev.wid == "cm-selector":
            selected_cmap = status["cm-selector"]["value"]
            im.set_cmap(selected_cmap)
            cbar_im.set_cmap(selected_cmap)
            # cm_name_label.set_label(selected_cmap)

            draw_canvas = True

        # when cm-kind dropdown menu is selected
        elif ev.wid == "cm-kind:select":
            kind = status["cm-kind"]["value"]
            cm_widgets, cm_names = get_colormap_widgets(kind)

            cmap_menu_items.replace_labels(cm_widgets, values=cm_names)

        # when norm is selected
        elif ev.wid == "norm-selector":
            norm_name = status["norm-selector"]["value"]
            print("norm", ev.wid, norm_name)
            im.set_norm(norms[norm_name]())
            cbar_im.set_norm(norms[norm_name]())
            draw_canvas = True

        if draw_canvas:
            wbm.fig.canvas.draw_idle()

        print(ev, status)

    wbm.set_callback(cb)

    wbm.install_all()

    plt.show()
