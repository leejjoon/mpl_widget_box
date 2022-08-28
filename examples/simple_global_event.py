import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            install_widgets_simple)

fig, ax = plt.subplots()
ax.plot([0, 1])

# Widgets to be added.
widgets = [
    W.Label("lbl", ""),
]

# A callback function which will be bound to any button-press event.
def cb(wbm, ev, status):
    lbl = wbm.get_widget_by_id("lbl")
    lbl.set_label("Installed")
    # if ev.wid == "btn":
    #     print("Button is pressed.")

wbm = install_widgets_simple(ax, widgets, cb)

plt.show()
