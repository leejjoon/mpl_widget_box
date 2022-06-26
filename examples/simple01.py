import numpy as np

import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            install_widgets_simple)


class Index:
    def __init__(self):
        self.ind = 0

    def inc(self):
        self.ind += 1
        return self.ind

    def dec(self):
        self.ind -= 1
        return self.ind


freqs = np.arange(2, 20, 3)
t = np.arange(0.0, 1.0, 0.001)
s = np.sin(2*np.pi*freqs[0]*t)

fig, ax = plt.subplots(num=2, clear=True)
l, = plt.plot(t, s, lw=2)
ax.set_title(f"freq = {freqs[0]}")

index = Index()

# We define simple widgets with two buttons.
widgets = [
    W.Button("btn-prev", "Prev", tooltip="Go to prev freq."),
    W.Button("btn-next", "Next", tooltip="Go to next freq."),
]

# A callback function.
def cb(wbm, ev: W.WidgetBoxEvent, status):
    if ev.wid == "btn-prev":
        i = index.dec()
    elif ev.wid == "btn-next":
        i = index.inc()
    else:
        i = index.ind

    i =  i % len(freqs)

    ydata = np.sin(2*np.pi*freqs[i]*t)
    l.set_ydata(ydata)

    ax.set_title(f"freq = {freqs[i]}")
    wbm.draw_idle()  # or you can simply do plt.draw()

# We need to keep the reference of the return value.
# If wbm gets deleted, the widgets will disappear.
wbm = install_widgets_simple(ax, widgets, cb)

plt.show()
