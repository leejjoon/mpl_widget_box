# mpl_widget_box

<img align="right" width="220px" src="https://user-images.githubusercontent.com/95962/180644553-9de7a6cf-8ad4-44fc-9aab-60138886ccd8.gif">

A simple gui widgets for matplotlib with a legend-like layout.

While Matplitlib does support gui-neutral widgets that work for any of the GUI
backends, it doesn't try to be too smart with respect to layout. The
mpl_widget_box try to be smarter using the OffsetBox that powers Matplotlib's
legends and annotations.

# Features

  * Gui-neutral widgets for Matplotlib
  * Layout behavior similar to legends.
  * Widgets are designed to minimize screen real estate when needed (e.g.,
    tooltips, dropdowns, popups, collapsable menu.).
  * Uses FontAwesome icons
  * Some of the Original Matplotlib's widgets are incorporated (e.g., Slider)
  * A single callback function that is called for any button-press events.

# A Simple Example

<img align="right" width="220px" src="https://user-images.githubusercontent.com/95962/180644581-73167b90-fda4-412f-a5dc-920d59d18d5d.png">

```python
import matplotlib.pyplot as plt

from mpl_widget_box import (widgets as W,
                            install_widgets_simple)

fig, ax = plt.subplots()
ax.plot([0, 1])

# Widgets to be added.
widgets = [
    W.Label("lbl", "Label"),
    W.Button("btn", "Button"),
]

# A callback function which will be bound to any button-press event.
def cb(wbm, ev, status):
    if ev.wid == "btn":
        print("Button is pressed.")

install_widgets_simple(ax, widgets, cb)

plt.show()
```

# Install

It is still in heavy development and is not available at pypi yet.
You may pip instal directly from the github repo,

```console
> pip install git+https://github.com/leejjoon/mpl_widget_box
```

or you may clone the repo locally and run

```console
> pip install .
```

