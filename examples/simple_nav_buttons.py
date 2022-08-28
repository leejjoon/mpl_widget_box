import matplotlib.pyplot as plt

from mpl_widget_box import install_widgets_simple
from mpl_widget_box.misc.nav_buttons import NavButtons


fig, ax = plt.subplots(1, 1)
ax.plot([0, 1])

nav_btn = NavButtons("nav", range(3))
nav_btn.lbl.patch.set_ec("0.8")

widgets = [
    nav_btn,
]

def cb(wbm, ev, status):
    i = nav_btn.process_event(wbm, ev, status)
    if i is not None:
        print(i)

wbm = install_widgets_simple(ax, widgets, cb=cb, loc=2)

plt.show()
