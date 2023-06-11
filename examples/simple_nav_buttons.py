from mpl_widget_box import install_widgets_simple
from mpl_widget_box.misc.nav_buttons import NavButtons

import numpy as np

def plot(fig):
    ax = fig.add_subplot(111)
    x = np.linspace(0, 1, 100)
    l1, = ax.plot(x, x)

    nav_btn = NavButtons("nav", ["0.5", "1  ", "2  "], label_width=30)

    widgets = [
        nav_btn,
    ]

    def cb(wbm, ev, status):
        v = nav_btn.process_event(wbm, ev, status)
        if v is not None:
            l1.set_data(x, np.power(x, float(v)))
            wbm.draw_idle()

    wbm = install_widgets_simple(ax, widgets, cb=cb, loc=2)

    return wbm

def main():
    import matplotlib.pyplot as plt
    fig = plt.figure()
    plot(fig)

    plt.show()

if __name__ == '__main__':
    main()
