import matplotlib.pyplot as plt
from mpl_widget_box import (widgets as W, install_widgets_simple)
import mpl_widget_box.axes_widget as AW

fig, ax = plt.subplots(1, num=1, clear=True)
ax.plot([0, 1])

label_width = 20
widgets = [W.Title("title", "Slider"),
           AW.SliderWidget("a", 0, 1),
           AW.SliderWidget("b", 0, 10, valinit=2, valfmt="{:.0f}"),
           AW.SliderWidget("c", 0, 1, label="C", tooltip="C"),
           AW.SliderWidget("d", 0, 1, label="DDD", label_width=25),
           AW.SliderWidget("e", 0, 1, label="E", label_width=25),
           AW.SliderWidget("f", 0, 1, overlay_alpha=0.9, label="F"),
           AW.SliderWidget("g", 0, 1,
                           value_overlay_on=False,
                           value_tooltip_on=False,
                           value_label_on=True),
           AW.RangeSliderWidget("h", 0, 1, label="H"),
           W.Button("go", "Go", expand=True, centered=True)
           ]

def cb(wbm, event, status):
    # r = status["rp"]["val"]
    # ax.plot([r], [r], "o")
    print(status)

wbm = install_widgets_simple(ax, widgets, cb=cb)

plt.show()
