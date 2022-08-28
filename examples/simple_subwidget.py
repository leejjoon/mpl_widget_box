import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            install_widgets_simple)


def test1():

    fig, ax = plt.subplots(num=2, clear=True)
    ax.plot([0, 1])

    sub_widgets = [
        W.Label("lbl", "-- Sub --"),
        W.Radio("radio", ["0", "1"]),
    ]

    widgets = [
        W.Sub("sub1", "Sub 1", sub_widgets),
        W.Sub("sub2", "Sub 2", sub_widgets, tooltip="Click to select"),
        W.Sub("sub3", "Sub 3", sub_widgets, where=""),
    ]

    def cb(wb, ev, status):
        print(ev, status)

    wbm = install_widgets_simple(ax, widgets, cb=cb, loc=2)

    plt.show()

if __name__ == "__main__":
    test1()
