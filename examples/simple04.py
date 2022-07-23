# Example showing multiple widgetboxes

import numpy as np

import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            WidgetBoxManager)

freqs = np.arange(2, 20, 3)
t = np.arange(0.0, 1.0, 0.001)
s = np.sin(2*np.pi*freqs[0]*t)

fig, ax = plt.subplots(num=2, clear=True)
l, = plt.plot(t, s, lw=2)


subwidgets1 = [
    W.HWidgets([
        W.Button("btn-prev", "left", tooltip="Go to prev freq."),
        W.Button("btn-next", "right", tooltip="Go to next freq."),
    ]),
]

radio_freq = W.Radio("radio-freq", [str(c) for c in freqs], selected=0)

subwidgets2 = [
    radio_freq
]


widgets = [
    W.RadioButton("menu-selector", ["  ", "Buttons", "Radio"],
                values=["empty", "menu1", "menu2"]),
]

wbm = WidgetBoxManager(fig)

wc_menu = wbm.add_anchored_widget_box(
    widgets,
    ax,
    loc=2,
    box_alignment=(0, 0),
    pad=(0, 0),
    bbox_to_anchor=ax,
    frameon=False
)


wc_sub = wbm.add_anchored_widget_box(
    [],
    ax,
    loc=2,
)
wc_sub.set_visible(False)

def cb(wbm: WidgetBoxManager, ev, status):
    if ev.wid == "menu-selector":
        selected = status["menu-selector"]["value"]
        wc_sub.set_visible(True)
        if selected == "menu1":
            subwidgets = subwidgets1
        elif selected == "menu2":
            subwidgets = subwidgets2
        else:
            subwidgets = []
            wc_sub.set_visible(False)

        wc_sub.reinit_widget_box(wbm, subwidgets)

    else:
        i = radio_freq.selected

        if ev.wid == "btn-prev":
            i -= 1
        elif ev.wid == "btn-next":
            i += 1

        i =  i % len(freqs)

        radio_freq.select(i)

        ydata = np.sin(2*np.pi*freqs[i]*t)
        l.set_ydata(ydata)

        wbm.draw_idle()

wbm.set_callback(cb)

wbm.install_all()

plt.show()
