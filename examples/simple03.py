import numpy as np

import matplotlib.pyplot as plt

from mpl_widget_box.widget_box import WidgetBoxManager

from typing import Dict
import mpl_widget_box.widgets as W


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

widgets = [
    W.HWidgets(
        [W.Button("btn-prev", "Prev", tooltip="Go to prev freq."),
         W.Button("btn-next", "Next", tooltip="Go to next freq.")]
    )
]


def cb(wbm: WidgetBoxManager, ev: W.WidgetBoxEvent, status: Dict):
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


wbm = WidgetBoxManager(fig)

wbm.add_anchored_widget_box(
    widgets,
    ax,
    loc=1,
    box_alignment=(1, 0),
    pad=(0, -3),
    bbox_to_anchor=ax,
    frameon=False
)

wbm.set_callback(cb)

wbm.install_all()

plt.show()
