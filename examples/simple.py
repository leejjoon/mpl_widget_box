import numpy as np

import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            install_widgets_simple)


def main():

    fig, ax = plt.subplots(num=2, clear=True)
    ax.plot([0, 1])

    sub_widgets = [
        W.Label("btn4", "-- Label --"),
        W.Radio("radio2", ["Ag3", "Bc3"]),
    ]

    widgets = [
        W.HWidgets(
            [
                W.Title("title0", "My Widgets"),
                W.Button("btn1", "X"),
            ]
        ),
        W.Title("title0", "My Widgets"),
        W.Button("btn1", "Click", mode="center", tooltip="Tooltip"),
        W.HWidgets([W.Button("btn2", "A"), W.Button("btn3", "B")]),
        W.CheckBox("check", ["1", "2", "3"], direction="h"),
        W.Radio("radio", ["Selection 1", "Selection 2"], title="Radio"),
        W.RadioButton("bar", ["A", "B", "C"]),
        W.Sub("sub1", "Sub", sub_widgets, tooltip="Sub"),
        W.HWidgets(
            [
                W.Label("label2", "dropdow"),
                W.Dropdown("dropdown", "Dropdown", ["123", "456"]),
            ],
            align="baseline",
        ),
    ]

    def cb(wb, ev, status):
        print(ev, status)

    wbm = install_widgets_simple(ax, widgets, cb=cb, loc=2)

    plt.show()
    return wbm


if __name__ == "__main__":
    main()
