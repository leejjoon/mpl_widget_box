import numpy as np

import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W, axes_widget as AW,
                            install_widgets_simple)


def main():

    fig, ax = plt.subplots(num=2, clear=True)
    ax.set_aspect(1.)
    ax.plot([0, 1])

    input1 = AW.TextAreaWidget("input1", "100", label="Value",
                               label_width=45)
    slider1 = AW.SliderWidget("slider1", 0, 1,
                              label="Slide", label_width=45)

    btn = W.Button("btn1", "Click", tooltip="Tooltip",
                   expand=True, align="center")

    widgets = [
        W.Title("title0", "MPL Widgets"),
        input1,
        slider1,
        btn,
    ]

    def cb(wb, ev, status):
        if ev.wid == "btn1":
            print(status)

    install_widgets_simple(ax, widgets, cb=cb)

    plt.show()


if __name__ == '__main__':
    main()

