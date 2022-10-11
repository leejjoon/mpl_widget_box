"""Example using `wait_for_button` method. This was meant to be used in the
interactive shell environent like ipython.
"""

import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            install_widgets_simple)

fig, ax = plt.subplots()
ax.plot([0, 1])

# Widgets to be added.
widgets = [
    W.Label("lbl", "Label"),
    W.Button("btn", "Button"),
    W.Button("quit", "Quit"),
]

# A callback function which will be bound to any button-press event.
def cb(wbm, ev, status):
    if ev.wid == "btn":
        print("A button is pressed")
    elif ev.wid == "quit":
        return True

wbm = install_widgets_simple(ax, widgets, cb)

while True:

    if l := wbm.wait_for_button():  # Note that wait_for_button returns True if
                                    # the figure is closed.
        if l:
            break

print("Done")

# plt.show()
