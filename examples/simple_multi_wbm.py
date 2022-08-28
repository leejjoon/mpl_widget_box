import numpy as np

import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            install_widgets_simple)
from mpl_widget_box.misc.nav_buttons import NavButtons


fig1, ax1 = plt.subplots(num=1, clear=True)
ax1.plot([0, 1])

nav_btn1 = NavButtons("nav", range(3))

widgets1 = [
    nav_btn1,
]

# A callback function.
def cb1(wbm, ev: W.WidgetBoxEvent, status):
    i = nav_btn1.process_event(wbm, ev, status)
    print("cb1", i)

wbm = install_widgets_simple(ax1, widgets1, cb1)

fig2, ax2 = plt.subplots(num=2, clear=True)
ax2.plot([0, 1])

nav_btn2 = NavButtons("nav", range(5, 10))

widgets2 = [
    nav_btn2,
]

# A callback function.
def cb2(wbm, ev: W.WidgetBoxEvent, status):
    i = nav_btn2.process_event(wbm, ev, status)
    print("cb2", i)

wbm2 = install_widgets_simple(ax2, widgets2, cb2)
plt.show()
