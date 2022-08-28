import numpy as np

import matplotlib.pyplot as plt
# import matplotlib.offsetbox
# matplotlib.offsetbox.DEBUG = True

from mpl_widget_box import (widgets as W,
                            widget_box as WB,
                            install_widgets_simple)
from mpl_widget_box.composite_widget import TitleCollapsable
fig, ax = plt.subplots(num=2, clear=True)

widgets = [
    TitleCollapsable("title", "My Widgets"),
    # W.Label("label", "TTTTTTTTTTTTTTTTTTTT"),
    W.Radio("radio", ["a", "b", "c"]),
]
title = widgets[0]

def cb(wbm: WB.WidgetBoxManager, e, status):
    title.process_event(wbm, e, status)

install_widgets_simple(ax, widgets, cb=cb)

plt.show()
