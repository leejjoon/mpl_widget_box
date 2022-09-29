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
    if ev.wid == "quit":
        return "quit"

wbm = install_widgets_simple(ax, widgets, cb)

# def wait_for_button():
#     if plt.fignum_exists(wbm.fig.number):
#         wbm.fig.waitforbuttonpress()
#         if wbm.get_last_callback_return_value():
#             return False
#         return True
#     else:
#         # return False if fig does not exists anymore.
#         return False

# plt.show()
while True:

    if l := wbm.wait_for_button():
        if l == "quit":
            break

print("Done")

# plt.show()
