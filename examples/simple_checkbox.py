import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            install_widgets_simple)


def test1():

    fig, ax = plt.subplots(num=2, clear=True)
    ax.plot([0, 1])

    widgets = [
        W.CheckBox("check1", ["1", "2"]),
        W.CheckBox("check1", ["1", "2"], direction="h"),
        W.CheckBox("check2", ["1", "2"],
                   title="Check", selected=[1]),
        W.CheckBox("check3", ["1", "2"], tooltips=["tooltip 1", "tooltip 2"],
                   selected=[0, 1]),
    ]

    def cb(wb, ev, status):
        print(ev, status)

    wbm = install_widgets_simple(ax, widgets, cb=cb, loc=2)

    plt.show()


if __name__ == "__main__":
    test1()
