import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            install_widgets_simple)

fig, ax = plt.subplots()
ax.plot([0, 1])

# Widgets to be added.
widgets = [
    W.HWidgets([W.Button("btn-disabled", "Disabled"),
                W.Button("btn-active", "Active")])
]

# # A callback function which will be bound to any button-press event.
def cb(wbm, ev, status):
    btn = wbm.get_widget_by_id("btn-disabled")
    btn.set_context("disabled")

#     lbl.set_label("Installed")
#     # if ev.wid == "btn":
#     #     print("Button is pressed.")

wbm = install_widgets_simple(ax, widgets, cb)

plt.show()
