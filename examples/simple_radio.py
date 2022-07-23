import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            install_widgets_simple)


def test1():

    fig, ax = plt.subplots(num=2, clear=True)
    ax.plot([0, 1])

    widgets = [
        W.Radio("radio1", ["1", "2"], title="Radio", selected=1),
        W.Radio("radio1", ["3", "4"], direction="h"),
        W.Radio("radio2", ["a", "b"], values=[1, 2]),
        W.Radio("radio3", ["1", "2"], tooltips=["tooltip 1", "tooltip 2"]),
    ]

    def cb(wb, ev, status):
        print(ev, status)

    wbm = install_widgets_simple(ax, widgets, cb=cb, loc=2)

    plt.show()


if __name__ == "__main__":
    test1()
