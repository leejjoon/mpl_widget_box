import numpy as np

import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            install_widgets_simple)


def test1():

    fig, ax = plt.subplots(num=2, clear=True)
    ax.plot(np.random.rand(10))

    sub_widgets = [
        W.Label("btn4", "-- Label --"),
        W.Radio("radio2", ["Ag3", "Bc3"]),
    ]

    widgets = [
        W.Title("title0", "My Widgets"),
        W.Sub("sub1", "Sub", sub_widgets, tooltip="Sub"),
        W.HWidgets(
            [
                W.Label("label2", "dropdow"),
                W.Dropdown("dropdown", "Dropdown", ["123", "456"]),
            ],
            align="baseline",
        ),
        W.Radio("radio", ["Ag", "Bc"]),
        W.CheckBox("check", ["1", "2", "3"], title="Check"),
        W.Button("btn1", "Click", centered=True, tooltip="Tooltip"),
        W.HWidgets([W.Button("btn2", "A"), W.Button("btn3", "B")]),
    ]

    def cb(wb, ev, status):
        print(ev, status)

    wbm = install_widgets_simple(ax, widgets, cb=cb, loc=2)

    plt.show()
    return wbm


if __name__ == "__main__":
    test1()
