import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            install_widgets_simple)

def get_da(w, h):
    import numpy as np
    import matplotlib.lines as mlines

    from matplotlib.offsetbox import DrawingArea

    da = DrawingArea(w, h, 0, 0)

    a = np.linspace(0, 1, w)
    l = mlines.Line2D(a * w, a*a * h, lw=3, color="0.5")
    da.add_artist(l)

    return da

def main():

    fig, ax = plt.subplots(num=2, clear=True)
    ax.plot([0, 1])

    da = get_da(20, 10)

    widgets = [
        W.Label("l1", "A"),
        W.Label("l2", "B", fixed_width=20, align="right"),
        W.Label("l3", "C", fixed_width=20,
                textprops=dict(weight="bold")),
        W.Label("l4", da, tooltip="simple graph"),
    ]

    widgets[0].patch.set_ec("r")

    widgets[1].patch.set_ec("r")
    # widgets[1]._expand = False
    # widgets[1]._align = "right"

    # widgets[2].patch.set_ec("r")
    # widgets[2]._align = "right"
    # widgets[0].box.frame.set_ec("g")

    def cb(wb, ev, status):
        if ev.wid == "l1":
            widgets[1].set_textprops(weight="bold")
        elif ev.wid == "l2":
            widgets[1].set_textprops(weight="normal")
        print(ev, status)

    install_widgets_simple(ax, widgets, cb=cb, loc=2)

    plt.show()


if __name__ == "__main__":
    main()
