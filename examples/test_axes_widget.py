import numpy as np

import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W, axes_widget as AW,
                            install_widgets_simple)


if True:

    fig, ax = plt.subplots(num=2, clear=True)
    ax.set_aspect(1.)
    ax.plot([0, 1])

    btn = W.Button("btn1", "Click", centered=True, tooltip="Tooltip")
    aw1 = AW.TextAreaWidget("input_min", "100", label="MIN",
                            label_width=35)
    slider1 = AW.SliderWidget("slider1", 0, 1,
                              label="Slide", label_width=35)

    widgets = [
        W.Title("title0", "My Widgets"),
        aw1,
        slider1,
        btn,
    ]

    # wbm.add_anchored_widget_box(
    #     widgets,
    #     ax,
    #     loc=2,
    #     # callback=cb
    # )

    def cb(wb, ev, status):
        if ev.wid == "btn1":
            print("clicked")
        print(ev.wid, status)

    install_widgets_simple(ax, widgets, cb=cb)

    plt.show()

