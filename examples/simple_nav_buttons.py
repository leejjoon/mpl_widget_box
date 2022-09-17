import matplotlib.pyplot as plt

from mpl_widget_box import install_widgets_simple
from mpl_widget_box.misc.nav_buttons import NavButtons

import numpy as np

fig, ax = plt.subplots(1, 1)
x = np.linspace(0, 1, 100)
l1, = ax.plot(x, x)

nav_btn = NavButtons("nav", [0.5, 1, 2])

widgets = [
    nav_btn,
]

def cb(wbm, ev, status):
    v = nav_btn.process_event(wbm, ev, status)
    if v is not None:
        l1.set_data(x, np.power(x, v))
        wbm.draw_idle()

wbm = install_widgets_simple(ax, widgets, cb=cb, loc=2)

plt.show()
