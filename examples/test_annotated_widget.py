import numpy as np
import matplotlib.pyplot as plt

from mpl_widget_box import WidgetBoxManager

from mpl_widget_box import (widgets as W,
                            install_widgets_simple)
from mpl_widget_box.widgets_impl import HWidgets

fig, ax1 = plt.subplots(1, 1, num=1, clear=True)
x = np.linspace(1., 2.5, 100)
y = np.zeros_like(x)
y[len(y)//2] = 1

# Widgets to be added.
widgets = [
    # W.Label("lbl", "Label"),
    # W.HWidgets([W.Button("btn", "<", tooltip="my tooltip"),]),
    W.RadioButton("radio", ["src", "bg"]),
    
]

# A callback function which will be bound to any button-press event.
def cb(wbm, ev, status):
    if ev.wid == "radio":
        print("Button is pressed.")

ax1.plot(x, y)

wbm = WidgetBoxManager(ax1.figure)

wbm.add_widget_box(
    widgets,
    ax1,
    xy=(1.5, 1.),
    xycoords=("data", "axes fraction"),
    xybox=(0, 0),
    box_alignment=(0.5, 0.5),
    frameon=False,
    clip=True,
)

if cb is not None:
    wbm.set_callback(cb)

wbm.install_all()

plt.show()

