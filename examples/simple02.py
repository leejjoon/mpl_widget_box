import numpy as np

import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            WidgetBoxManager,
                            install_widgets_simple)

from mpl_widget_box.fa_helper import get_fa_textarea, FontAwesome

# By default, only a limited set of icon names are loaded. If you want to use
# full icon set, you need to manually load the icon names and use. It will use
# ryml module if available get fall back to yaml. ryml is fater in its loading
# speed.
try:
    import ryml
except ImportError:
    ryml = None

if ryml:
    icons = FontAwesome.load_icons_ryml()
else:
    icons = FontAwesome.load_icons_yaml()


freqs = np.arange(2, 20, 3)
t = np.arange(0.0, 1.0, 0.001)
s = np.sin(2*np.pi*freqs[0]*t)

fig, ax = plt.subplots(num=2, clear=True)
l, = plt.plot(t, s, lw=2)

# fontawesome icons can be used as a label
btn_up = get_fa_textarea(icons["caret-up"], color="w")
btn_down = get_fa_textarea(icons["caret-down"], color="w")

widgets = [
    W.Radio("radio-freq", [str(c) for c in freqs], selected=0),
    W.HWidgets([
        W.Button("btn-prev", btn_up, tooltip="Go to prev freq."),
        W.Button("btn-next", btn_down, tooltip="Go to next freq."),
    ]),
]


def cb(wbm: WidgetBoxManager, ev: W.WidgetBoxEvent, status):

    w = wbm.get_widget_by_id("radio-freq")
    i = w.selected

    if ev.wid == "btn-prev":
        i -= 1
    elif ev.wid == "btn-next":
        i += 1

    i = w.select(i) # select method will wrap around i if required.

    ydata = np.sin(2*np.pi*freqs[i]*t)
    l.set_ydata(ydata)

    wbm.draw_idle()  # or you can simply do plt.draw()

wbm = install_widgets_simple(ax, widgets, cb)

plt.show()
