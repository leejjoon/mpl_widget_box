import numpy as np

import matplotlib.pyplot as plt
# import matplotlib.offsetbox
# matplotlib.offsetbox.DEBUG = True

from mpl_widget_box import (widgets as W,
                            widget_box as WB,
                            install_widgets_simple)

from mpl_widget_box.composite_widget import (TitleCollapsableWithVisibility
                                             as TitleCollapsable)
fig, ax = plt.subplots(num=2, clear=True)

title = TitleCollapsable("title", "My Widgets")
widgets = [
    title,
    W.Radio("radio", ["a", "b", "c"]),
    W.Button("btn", "Button", expand=True, align="center"),
]

def cb(wbm: WB.WidgetBoxManager, e, status):
    title.process_event(wbm, e, status)

install_widgets_simple(ax, widgets, cb=cb)

plt.show()
